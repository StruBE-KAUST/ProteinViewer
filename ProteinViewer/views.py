from django.shortcuts import render
from django.views.generic import View
from django.contrib import messages
from django.conf import settings

from .forms import SubmitViewerDataForm

import logging
import os
import subprocess
from subprocess import Popen, PIPE, STDOUT

from getLinker import getLinker

import Biskit as B
import re
import time



class SubmitPdbFileView(View):
    """Main view to render the form if GET or error in POST
    render the VR viewer if no error in POST."""
    count = 0


    @staticmethod
    def render_form(request, form=None):
        """Render form."""
        log = logging.getLogger(__name__)
        log.debug("Enter with args: " + str(request) + " ; " + str(form))

        if form is None:
            form = SubmitViewerDataForm()

        response_data = render(
                request,
                'ProteinViewer/submit.html',
                {
                    'form': form,
                })

        log.debug("Exit")
        return response_data

    def get(self, request):
        """Serve the form to submit a PDB file."""
        return self.render_form(request)

    def post(self, request):
        """Serve the viewer page if valid form, else serve the form."""
        log = logging.getLogger(__name__)
        log.debug("Enter with args: " + str(request))

        form = SubmitViewerDataForm(
                request.POST,
                request.FILES)

        if form.is_valid():
            log.debug("Valid form")

            try:
                response = self.generate_viewer_page(request)
            except Exception as e:
                log.error("Error when trying to generate viewer page")
                log.error(e)
                response = self.render_form(request, form)
                messages.error(request, "An unexpected error occurred.")
        else:
            log.debug("Invalid form")
            messages.error(request, "Please check the form.")
            response = self.render_form(request, form)

        log.debug("Exit")
        return response

    def generate_viewer_page(self, request):

        starttime = time.time()

        rep = 'surf' # TODO: take representation from the form using request.REP / smth

        # TODO: save this in a new, session-specific file within MEDIA_ROOT.
        # maybe static count for file name?

        # PDB files are stored in MEDIA_ROOT as pdb0.pdb, pdb1.pdb, ...
        for count, u_file in enumerate(request.FILES.getlist('pdb_files')):
            with open(os.path.join(settings.MEDIA_ROOT, 'pdb' + str(count) + '.pdb'), 'wb+') as destination:
                for chunk in u_file:
                    destination.write(chunk)
            # with open(os.path.join(settings.MEDIA_ROOT, 'pdb' + str(count) + 'ori.pdb'), 'wb+') as destination:
            #     for chunk in u_file:
            #         destination.write(chunk)

        # TODO: parse the input to get just the sequence string.. cause they could
        # upload the whole fasta file including that top line with the >
        sequence = request.POST['sequence']

        with open(os.path.join(settings.MEDIA_ROOT, 'sequence.fasta'), 'wb+') as destination:
            for chunk in request.POST['sequence']:
                destination.write(chunk)


        domRanges = []
        domSpans = []

        for i in xrange(len(request.FILES.getlist('pdb_files'))):
            m = B.PDBModel('%s' %(settings.MEDIA_ROOT) + 'pdb' + str(i) + '.pdb')
            m = m.compress(m.maskProtein())
            s = m.sequence()

            match = re.search(s, sequence)
            domR = match.span()
            domR = [domR[0], domR[1]]
            domRanges.append(domR)
       
        prev = 0
        allRanges = []

        for i in xrange(len(domRanges)):
            dom = domRanges[i]
            if dom[0] == prev and prev == 0:
                allRanges.append(dom)
                prev = dom[1]
            elif dom[0] != prev and prev == 0:
                tup = [prev, dom[0] + 1]
                allRanges.append(tup)
                allRanges.append(dom)
                prev = dom[1]
            elif dom[0] != prev:
                tup = [prev - 1, dom[0] + 1]
                allRanges.append(tup)
                allRanges.append(dom)
                prev = dom[1]
            elif i != len(domRanges) - 1:
                tup = [dom[0] - 1, dom[0] + 1]
                allRanges.append(tup)
                prev = dom[1]
            else:
                tup = [dom[0] - 1, dom[1]]
                allRanges.append(tup)
                prev = dom[1]

        ranges = [domRanges, allRanges]

        print '!!!! \n \n \n \n '
        print domRanges
        print allRanges

        pieces = getLinker(domRanges, allRanges, True, 0, 'sequence.fasta') #TODO: take representation as well
        
        # TODO: if pieces == 0 (because ranch found the domains to be too far
        # away from eachother), throw an error to make the user upload new domains

        if pieces == 0: 
            response = self.render_form(request, form)
            messages.error(request, "An unexpected error occurred.")
            return response


        domains = pieces[0]
        linkers = pieces[1]

        asset_string = ""
        entity_string = ""

        # TODO: Add hulls to the asset string when meshlab is up and running
        # don't give the hulls an mtl file and use the material property instead
        # to be able to set transparency and opacity (make invisible!)
        for i in xrange(domains):
            obj_name = 'dom' + str(i) + '.obj'
            mtl_name = 'dom' + str(i) + '.mtl'
            assets = '<a-asset-item id="dom_model' + str(i) + '\" src="../media/models/' + obj_name + '\"></a-asset-item>' + '<a-asset-item id="dom_mat' + str(i) + '" src="../media/models/' + mtl_name + '"></a-asset-item>' 
            entities = '<a-entity id="dom' + str(i) + '\" mixin="dymol" class="domain" obj-model="obj: #dom_model' + str(i) + '; mtl: #dom_mat' + str(i) + '\"></a-entity>'
            asset_string = asset_string + assets
            entity_string = entity_string + entities

        for i in xrange(linkers):
            obj_name = 'link' + str(i) + '.0.obj'
            mtl_name = 'link' + str(i) + '.0.mtl'
            assets = '<a-asset-item id="link_model' + str(i) + '\" src="../media/models/' + obj_name + '\"></a-asset-item>' + '<a-asset-item id="link_mat' + str(i) + '" src="../media/models/' + mtl_name + '"></a-asset-item>' 
            entities = '<a-entity id="link' + str(i) + '\" mixin="dylink" class="linker" obj-model="obj: #link_model' + str(i) + '; mtl: #link_mat' + str(i) + '\"></a-entity>'
            asset_string = asset_string + assets
            entity_string = entity_string + entities

        # send render request with context to the template
        context = {'assets': asset_string, 'entities': entity_string, 'count': pieces, 'ranges': ranges}
        
        endtime = time.time()

        wholetime = endtime - starttime
        print 'Whole process takes ' + str(wholetime) + ' to run'

        return render(request, 'ProteinViewer/viewer.html', context)
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

        rep = 'surf' # TODO: take representation from the form using request.REP / smth
        # TODO: get number of domains from form
        # TODO: get domain ranges from form. Store as a list of tuples (start, end)
        # TODO: get sequence from form.

        name = 'pdb'
        obj_name = name + '.obj'
        mtl_name = name + '.obj.mtl'

        # temporarily define sequence, rep, num of domains & domain ranges here
        # NOTE about domain ranges:: take residue range off sequence, NOT pdb file
        # so if the user is asked to select the range of the sequence that's in each
        # domain it'd be best. Or if they give the residue numbers from the sequence
        # ## just working inside getLinker()


        # TODO: save this in a new, session-specific file within MEDIA_ROOT.
        # maybe static count for file name?

        # PDB files are stored in MEDIA_ROOT as pdb.pdb1, pdb.pdb2, ...
        for count, u_file in enumerate(request.FILES.getlist('pdb_files')):
            with open(os.path.join(settings.MEDIA_ROOT, name + str(count) + '.pdb'), 'wb+') as destination:
                for chunk in u_file:
                    destination.write(chunk)

        # TODO: parse the input to get just the sequence string.. cause they could
        # upload the whole fasta file including that top line with the >
        sequence = request.POST['sequence']

        with open(os.path.join(settings.MEDIA_ROOT, 'sequence.fasta'), 'wb+') as destination:
            for chunk in request.POST['sequence']:
                destination.write(chunk)


        domRanges = []

        for i in xrange(len(request.FILES.getlist('pdb_files'))):
            m = B.PDBModel('%s' %(settings.MEDIA_ROOT) + name + str(i) + '.pdb')
            s = m.sequence()

            print s

            match = re.search(s, sequence)
            domR = match.span()
            domR = (domR[0], domR[1])
            domRanges.append(domR)

        print domRanges

        getLinker(domRanges, 'sequence.fasta') #TODO: take list of domains, domain ranges, and sequence file (not sequence string that we have right now)

        # TODO: Clean the pdb, center the pdb, then use domain ranges and number of domains
        # to cut the given pdb up (use for # of domains for loop for pdb naming?).

        # TODO: pass list of generated pdbs and the sequence file to getLinker().

        # want to be able to use this function whenever we update the positions
        # of the domains. So, it will use individual pdbs for each domain
        # getLinker() #TODO: take list of domains, domain ranges, and sequence file

        # send render request with context to the template
        context = {'obj_file': obj_name, 'mtl_file': mtl_name} # add everything to context..
        return render(request, 'ProteinViewer/viewer.html', context)

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
                response = self.generate_viewer_page(request, form)
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

    def generate_viewer_page(self, request, form):

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

        for i in xrange(len(request.FILES.getlist('pdb_files'))):
            m = B.PDBModel('%s' %(settings.MEDIA_ROOT) + 'pdb' + str(i) + '.pdb')
            m = m.compress(m.maskProtein())
            s = m.sequence()

            match = re.search(s, sequence)
            domR = match.span()
            domR = [domR[0], domR[1]]
            domRanges.append(domR)
       
        prev = 0
        end = len(sequence)
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

        if(allRanges[len(allRanges) - 1])[1] != end:
            tup = [prev - 1, end]

        print allRanges 

        ranges = [domRanges, allRanges]

        pieces = getLinker(domRanges, allRanges, True, 0, 'sequence.fasta') #TODO: take representation as well
        
        # TODO: if pieces == 0 (because ranch found the domains to be too far
        # away from eachother), throw an error to make the user upload new domains

        if pieces == 0: 
            response = self.render_form(request, form)
            messages.error(request, "Domains are too far apart!")
            return response

        domains = pieces[0]
        linkers = pieces[1]

        # use domranges and allranges to get the extremes of each pdb file that
        # was produced in getLinker
        linkRanges = []

        for i in allRanges:
            if i in domRanges:
                pass
            else: 
                linkRanges.append(i)


        # TRYING a different approach here; one that looks at the linker-domain
        # pattern only to determine which domain the boxes stick to and which
        # box to use in the first place.

        # if linkRanges[0] == allRanges[0] and linkRanges[len(linkRanges) - 1] == allRanges[len(allRanges) - 1] # case 1
        # if linkRanges[0] == allRanges[0] # case 2
        # if linkRanges[len(linkRanges) - 1] == allRanges[len(allRanges) - 1] # case 3
        # else # case 4

        # what to do in those other cases.. cut the linker from linkRanges?
        # till we end up with a list that only has the middle linkers? And then go
        # by odd even to find out which domain to stick to and whether to use the
        # green or white..? BRILLIANT

        linkShift = 0
        if linkRanges[0] == allRanges[0]:
            linkRanges.remove(linkRanges[0])
            linkShift = 1
        if linkRanges[len(linkRanges) - 1] == allRanges[len(allRanges) - 1]:
            linkRanges.remove(linkRanges[len(linkRanges) - 1])

        # by here, linkRanges only contains the ranges for the middle linkers

        # now, from all the domains get all the start and end residues
        startPos = []
        endPos = []

        for i in xrange(domains):
            m = B.PDBModel("%spieces/dom" %(settings.MEDIA_ROOT) + str(i) + '.pdb')
            domR = domRanges[i]
            shift = domR[0]
            extremes = [domR[0] - shift, domR[1] - shift - 1]
            start = m.takeResidues([extremes[0]])
            end = m.takeResidues([extremes[1]])
            startXyz = start.getXyz()*0.05
            first = startXyz[0].tolist()
            endXyz = end.getXyz()*0.05
            # endXyz[0] seems to be better even though endXyz[len(endXyz) - 1] is the actual end..
            end = endXyz[len(endXyz) - 1].tolist()
            if i != 0:
                startPos.append(first)
            if i != domains - 1:
                endPos.append(end)


        domNum = 0
        linkNum = 0

        boxDeets = []

        for i in xrange(len(linkRanges)*2):
            if i % 2 == 0:
                # if even, take endpos and link to domain number
                boxDeets.append([endPos[0], domNum])
                endPos.remove(endPos[0])
            else:
                # if odd, up the domain number, take startpos and link to num
                domNum = domNum + 1
                boxDeets.append([startPos[0], domNum])
                startPos.remove(startPos[0])

        print boxDeets

        asset_string = ""
        entity_string = ""

        # TODO: Add hulls to the asset string when meshlab is up and running
        # don't give the hulls an mtl file and use the material property instead
        # to be able to set transparency and opacity (make invisible!)

        # TODO: Put "follow" on the molecule, NOT on the hull!

        for i in xrange(domains):
            obj_name = 'dom' + str(i) + '.obj'
            mtl_name = 'dom' + str(i) + '.mtl'
            assets = '<a-asset-item id="dom_model' + str(i) + '\" src="../media/models/' + obj_name + '\"></a-asset-item>' + '<a-asset-item id="dom_mat' + str(i) + '" src="../media/models/' + mtl_name + '"></a-asset-item>' 
            entities = '<a-entity id="dom' + str(i) + '" mixin="dymol" class="domain" obj-model="obj: #dom_model' + str(i) + '; mtl: #dom_mat' + str(i) + '"></a-entity>'
            asset_string = asset_string + assets
            entity_string = entity_string + entities
            # TODO: uncomment the code below when transfer code to a linux system and
            # meshlabserver works to produce the required hull colliders:
            # hobj_name = 'hull' + str(i) + '.obj'
            # hmtl_name = 'hull' + str(i) + '.obj.mtl'

        for i in xrange(linkers):
            obj_name = 'link' + str(i) + '.0.obj'
            mtl_name = 'link' + str(i) + '.0.mtl'
            assets = '<a-asset-item id="link_model' + str(i) + '\" src="../media/models/' + obj_name + '\"></a-asset-item>' + '<a-asset-item id="link_mat' + str(i) + '" src="../media/models/' + mtl_name + '"></a-asset-item>' 
            entities = '<a-entity id="link' + str(i) + '\" mixin="dylink" class="linker" obj-model="obj: #link_model' + str(i) + '; mtl: #link_mat' + str(i) + '\"></a-entity>'
            asset_string = asset_string + assets
            entity_string = entity_string + entities

        # PROBLEM:: Need to find out how to relate the box to the domain!! Which domain
        # should it "follow", and how do we keep track?? Because a single domain can have 
        # either 0, 1 or 2!!
        # for i in xrange(len(startBoxes)):
        #     # TODO: Add follow="target: dom' + str(i) + '" at the end of the string, right before the >
        #     box = '<a-box id="box' + str(i) + '" mixin="cube" class="collision" position="' + str(startBoxes[i][0]) + ' ' + str(startBoxes[i][1]) + ' ' + str(startBoxes[i][2]) + '" material="color: white" static-body collision-filter="group: default" ></a-box>'
        #     entity_string = entity_string + box

        # for i in xrange(len(endBoxes)):
        #     # TODO: Add follow="target: dom' + str(i) + '" at the end of the string, right before the >
        #     box = '<a-box id="box' + str(i) + '" mixin="cube" class="collision" position="' + str(endBoxes[i][0]) + ' ' + str(endBoxes[i][1]) + ' ' + str(endBoxes[i][2]) + '" material="color: green" static-body collision-filter="group: default" ></a-box>'
        #     entity_string = entity_string + box

        lineNum = 0
        for i in xrange(len(boxDeets)):
            # use a component to relate the box to the line and linker..?
            box = ""
            if i % 2 == 0:
                box = '<a-entity id="box' + str(i) + '" mixin="cube" class="collision" position="' + str(boxDeets[i][0][0]) + ' ' + str(boxDeets[i][0][1]) + ' ' + str(boxDeets[i][0][2]) + '" material="transparent: true; opacity: 0" follow="target: dom' + str(boxDeets[i][1]) + '" line="' + str(linkNum) + '" link="' + str(linkNum + linkShift) + '"></a-entity>'
                # box = '<a-box id="box' + str(i) + '" mixin="cube" class="collision" position="' + str(boxDeets[i][0][0]) + ' ' + str(boxDeets[i][0][1]) + ' ' + str(boxDeets[i][0][2]) + '" material="transparent: true; opacity: 0" follow="target: dom' + str(boxDeets[i][1]) + '" linkline="' + str(linkNum) + '"></a-box>'
            else:
                box = '<a-entity id="box' + str(i) + '" mixin="cube" class="collision" position="' + str(boxDeets[i][0][0]) + ' ' + str(boxDeets[i][0][1]) + ' ' + str(boxDeets[i][0][2]) + '" material="transparent: true; opacity: 0" follow="target: dom' + str(boxDeets[i][1]) + '" line="' + str(linkNum) + '" link="' + str(linkNum + linkShift) + '"></a-entity>'
                #box = '<a-box id="box' + str(i) + '" mixin="cube" class="collision" position="' + str(boxDeets[i][0][0]) + ' ' + str(boxDeets[i][0][1]) + ' ' + str(boxDeets[i][0][2]) + '" material="transparent: true; opacity: 0" follow="target: dom' + str(boxDeets[i][1]) + '" linkline="' + str(linkNum) + '"></a-box>'
                linkNum = linkNum + 1
            entity_string = entity_string + box

        # depending on how many boxes there are, create lines to go in between them
        # there should be an even number of boxes!

        lineCount = len(boxDeets)/2
        for i in xrange(lineCount):
            line = '<a-entity id="line' + str(i) + '" class="line" line="start: 0 0 0; end: 0 0 0; color: #00ff00" startbox="box' + str(i*2) + '" endbox="box' + str(i*2+1) + '"></a-entity>'
            entity_string = entity_string + line

        # send render request with context to the template
        context = {'assets': asset_string, 'entities': entity_string, 'count': pieces, 'ranges': ranges, 'lines': lineCount, 'shift': linkShift}
        
        endtime = time.time()

        wholetime = endtime - starttime
        print 'Whole process takes ' + str(wholetime) + ' to run'

        return render(request, 'ProteinViewer/viewer.html', context)
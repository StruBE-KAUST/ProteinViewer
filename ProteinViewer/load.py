"""
Processes data from form, then calls getLinker to run ranch/pulchra/vmd etc
and returns the viewer page
"""

from django.shortcuts import render
from models import DbEntry
from django.conf import settings
from ast import literal_eval

from django.http import HttpResponseNotFound

import time
import Biskit as B
import re

from getLinker import getLinker
from views import SubmitPdbFileView

from django.http import HttpResponseForbidden


def findDoms(pdbs, tempDir, sequence):
	"""
	Find the residue ranges for each domain using the pdb files and sequence
	@param pdbs: number of domains
	@type pdbs: int
	@param tempDir: directory where files are located
	@type tempDir: string
	@param sequence: the sequence for the file
	@type sequence: string

	@return domRanges: the residue ranges for each domain
	@rtype domRanges: list of lists
	"""

	domRanges = []

	for i in xrange(int(pdbs)):
	    m = B.PDBModel('%s' %(tempDir) + '/pdb' + str(i) + '.pdb')
	    m = m.compress(m.maskProtein())
	    s = m.sequence()

	    match = re.search(s, sequence)
	    domR = match.span()
	    domR = [domR[0], domR[1]]
	    domRanges.append(domR)

	return domRanges

def findAll(domRanges, sequence):
	"""
	Use the domain ranges and the sequence to find the linkers' residue ranges
	@param domRanges: the residue ranges for all domains
	@type: list
	@param sequence: the sequence for the file
	@type: string

	@return allRanges: residue ranges for all domains and linkers
	@rtype: list of lists
	"""

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
	    allRanges.append(tup)

	return allRanges


def getBoxDeets(domRanges, linkRanges, allRanges):
	"""
	Use the domain-linker pattern to determine which domains the boxes (which
	indicate the domain-linker boundary) will follow. There are 4 cases:
	Case #1: linkRanges[0] == allRanges[0] and linkRanges[len(linkRanges) - 1] == allRanges[len(allRanges) - 1]
			 (ie. there is a leading linker and a trailing linker)
	Case #2: linkRanges[0] == allRanges[0]
			 (ie. there is a leading linker but no trailing linker)
	Case #3: linkRanges[len(linkRanges) - 1] == allRanges[len(allRanges) - 1]
			 (ie. there is a trailing linker but no leading linker)
	Case #4: else
			 (there is no leading or training linker)

	@param domRanges: the residue ranges for all domains
	@type domRanges: list
	@param linkRanges: the residue ranges for all linkers
	@type: linkRanges: list
	@param: allRanges: the residue ranges for all domains and linkers
	@type: allRanges: list

	@return boxDeets: list of the x,y,z positions of all the 
	"""

	# remove trailing linkers from linkRanges, keeping track of leading ones 
	linkShift = 0
	if linkRanges[0] == allRanges[0]:
	    linkRanges.remove(linkRanges[0])
	    linkShift = 1
	if linkRanges[len(linkRanges) - 1] == allRanges[len(allRanges) - 1]:
	    linkRanges.remove(linkRanges[len(linkRanges) - 1])

	startPos = []
	endPos = []

	# get the position of the start and end residues of each domain
	for i in xrange(domains):
	    m = B.PDBModel("%s/dom" %(tempDir) + str(i) + '.pdb')
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




def load(request, form_id):
	"""
	Uses the user-entered values to get the residue ranges, then calls getLinker.
	Returns the viewer page with values in the context
	@param request: the request from views.py
	@param form_id: the unique identifier for the form
	@type form_id: string
	"""

	# check if session matches user
	obj = DbEntry.objects.get(form_id = form_id)
	session = request.session.session_key

	origin = obj.sessionId
	
	if origin != session:
		return HttpResponseForbidden()

	pdbs = obj.pdbs
	rep = obj.rep.encode('ascii')
	sequence = obj.sequence.encode('ascii')
	form_id = form_id.encode('ascii')
	tempDir = settings.MEDIA_ROOT + form_id

	starttime = time.time()
	domRanges = findDoms(pdbs, tempDir, sequence)
	allRanges = findAll(domRanges, sequence)

	pieces = getLinker(domRanges, allRanges, True, 0, 'sequence.fasta', rep, tempDir)
	
	if pieces == 0: 
		# ranch was killed; domains too far apart
	    response = self.render_form(request, form)
	    # TODO: Go back to the form and make the user upload new domains
	    messages.error(request, "Domains are too far apart!")
	    return response

	domains = pieces[0]
	linkers = pieces[1]

	# use domranges and allranges to sort for linkers' residue ranges
	linkRanges = []

	for i in allRanges:
	    if i in domRanges:
	        pass
	    else: 
	        linkRanges.append(i)

	boxDeets = getBoxDeets(domRanges, linkRanges, allRanges, tempDir)

	asset_string = ""
	entity_string = ""

	# TODO: Add hulls to the asset string when meshlab is up and running
	# don't give the hulls an mtl file and use the material property instead
	# to be able to set transparency and opacity (make invisible!) 
	# Put "follow" on the molecule, NOT on the hull!

	# create the domain entities
	for i in xrange(domains):
	    obj_name = 'dom' + str(i) + '.obj'
	    mtl_name = 'dom' + str(i) + '.mtl'
	    assets = '<a-asset-item id="dom_model' + str(i) + '\" src="/media/%s/' %(form_id) + obj_name + '\"></a-asset-item>' + '<a-asset-item id="dom_mat' + str(i) + '" src="/media/%s/' %(form_id) + mtl_name + '"></a-asset-item>' 
	    entities = '<a-entity id="dom' + str(i) + '" mixin="dymol" class="domain" obj-model="obj: #dom_model' + str(i) + '; mtl: #dom_mat' + str(i) + '"></a-entity>'
	    asset_string = asset_string + assets
	    entity_string = entity_string + entities

	# create the linker entities
	for i in xrange(linkers):
	    obj_name = 'link' + str(i) + '.0.obj'
	    mtl_name = 'link' + str(i) + '.0.mtl'
	    assets = '<a-asset-item id="link_model' + str(i) + '\" src="/media/%s/' %(form_id) + obj_name + '\"></a-asset-item>' + '<a-asset-item id="link_mat' + str(i) + '" src="/media/%s/' %(form_id) + mtl_name + '"></a-asset-item>' 
	    entities = '<a-entity id="link' + str(i) + '\" mixin="dylink" class="linker" obj-model="obj: #link_model' + str(i) + '; mtl: #link_mat' + str(i) + '\"></a-entity>'
	    asset_string = asset_string + assets
	    entity_string = entity_string + entities

	# create the box entities,and relate them to the domains, lines and linkers
	# that they are associated with
	for i in xrange(len(boxDeets)):
	    box = ""
	    if i % 2 == 0:
	        box = '<a-entity id="box' + str(i) + '" mixin="cube" class="collision" position="' + str(boxDeets[i][0][0]) + ' ' + str(boxDeets[i][0][1]) + ' ' + str(boxDeets[i][0][2]) + '" material="transparent: true; opacity: 0" follow="target: dom' + str(boxDeets[i][1]) + '" line="' + str(linkNum) + '" link="' + str(linkNum + linkShift) + '"></a-entity>'
	    else:
	        box = '<a-entity id="box' + str(i) + '" mixin="cube" class="collision" position="' + str(boxDeets[i][0][0]) + ' ' + str(boxDeets[i][0][1]) + ' ' + str(boxDeets[i][0][2]) + '" material="transparent: true; opacity: 0" follow="target: dom' + str(boxDeets[i][1]) + '" line="' + str(linkNum) + '" link="' + str(linkNum + linkShift) + '"></a-entity>'
   	        linkNum = linkNum + 1
	    entity_string = entity_string + box

	# create lines to go between the boxes; there will always be an even number of boxes
	lineCount = len(boxDeets)/2
	for i in xrange(lineCount):
	    line = '<a-entity id="line' + str(i) + '" class="line" line="start: 0 0 0; end: 0 0 0; color: #00ff00" startbox="box' + str(i*2) + '" endbox="box' + str(i*2+1) + '"></a-entity>'
	    entity_string = entity_string + line

	# create context for the render request
	context = {'assets': asset_string, 'entities': entity_string, 'count': pieces, 'ranges': ranges, 'lines': lineCount, 'shift': linkShift, 'rep': rep, 'temp': tempDir, 'form_id': form_id}

	endtime = time.time()

	wholetime = endtime - starttime
	print 'Whole process takes ' + str(wholetime) + ' to run'

	return render(request, 'ProteinViewer/viewer.html', context)
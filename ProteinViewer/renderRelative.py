"""
Uses information from pdb files to render the .obj files in a-frame relative
to one another so that the pieces look like a whole molecule together but can
still be manipulated per piece
"""

import Biskit as B
from django.conf import settings
from .apps import VMDConfig
from .apps import MeshlabConfig
import json
from django.http import HttpResponse

import os
import subprocess
from subprocess import Popen, PIPE, STDOUT
import logging

from models import DbEntry

def renderRelative(request, form_id):
	"""
	@param form_id: the form id taken from the request url
	@type form_id: unicode
	"""

	# check if session matches user
	obj = DbEntry.objects.get(form_id = form_id)
	session = request.session.session_key

	origin = obj.sessionId
	
	if origin != session:
		print 'oops'
		# TODO: return a different error, showing that session doesn't match user
		return HttpResponseNotFound('<h1>Page not found</h1>')


	log = logging.getLogger(__name__)

	domains = request.POST.get('domains')
	linkers = request.POST.get('linkers')
	grabNum = request.POST.get('grabNum')
	presses = request.POST.get('presses')
	tempDir = request.POST.get('temp')

	dompoints = []
	linkpoints = []
	# get the positions of the center of each domain and linker. Since the 
	# pdb file had been centered before splitting, this gives us the coordinates
	# relative to the center. *0.05 to turn the pdb 
	for i in xrange(int(domains)):
		file = '%s/dom' %(tempDir) + str(i) + '.pdb'
		file = str(file)
		log.info(file)
		log.info(os.stat(file))
		domain = B.PDBModel(file)
		center = domain.center()*0.05
		dompoints.append(json.dumps(center.tolist()))

	for i in xrange(int(linkers)):
		file = '%s/link' %(tempDir) + str(i) + '.' + str(grabNum) + '.pdb'
		file = str(file)
		linker = B.PDBModel(file)
		center = linker.center()*0.05
		linkpoints.append(json.dumps(center.tolist()))

	json_array = json.dumps([presses, dompoints, linkpoints])

	return HttpResponse(json_array, content_type="application/json")
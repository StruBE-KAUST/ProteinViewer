"""
Uses information from pdb files to render the .obj files in a-frame relative
to one another so that the pieces look like a whole molecule together but can
still be manipulated per piece
"""

import Biskit as B
import json

import os
import logging

from models import ViewingSession
from django.http import HttpResponseForbidden
from django.http import HttpResponse


def renderRelative(request, form_id):
	"""
	Determines positions in a-frame to place each domain and linker so that
	they are rendered relative to one another
	@param form_id: the form id taken from the request url
	@type form_id: unicode

	@return: HttpResponseObject
	"""

	# check if session matches user
	current_viewing_session = ViewingSession.objects.get(form_id = form_id)
	session_id = request.session.session_key

	original_session_id = current_viewing_session.session_id
	
	if original_session_id != session_id:
		return HttpResponseForbidden()

	log = logging.getLogger(__name__)

	number_of_domains = current_viewing_session.number_of_domains
	number_of_linkers = current_viewing_session.number_of_linkers
	temporary_directory = current_viewing_session.temporary_directory

	version = request.POST.get('version')
	presses = request.POST.get('presses')
	do_all = request.POST.get('do_all')

	domain_positions = []
	linker_positions = []
	# get the positions of the center of each domain and linker. Since the 
	# pdb file had been centered before splitting, this gives us the coordinates
	# relative to the center. *0.05 to turn the pdb coordinates into aframe coordinates
	if int(do_all) == 0:
		for i in xrange(number_of_domains):
			file = '{}/dom'.format(temporary_directory) + str(i) + '.pdb'
			file = str(file)
			log.info(file)
			log.info(os.stat(file))
			domain = B.PDBModel(file)
			center = domain.center()*0.05
			domain_positions.append(json.dumps(center.tolist()))

	for i in xrange(number_of_linkers):
		file = '{}/link'.format(temporary_directory) + str(i) + '.' + str(version) + '.pdb'
		file = str(file)
		log.info(file)
		log.info(os.stat(file))
		linker = B.PDBModel(file)
		center = linker.center()*0.05
		linker_positions.append(json.dumps(center.tolist()))

	json_array = json.dumps([presses, domain_positions, linker_positions])

	return HttpResponse(json_array, content_type="application/json")
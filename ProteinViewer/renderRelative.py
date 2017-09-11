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

def renderRelative(request):

	log = logging.getLogger(__name__)
	dompoints = []
	linkpoints = []
	domains = request.POST.get('domains')
	linkers = request.POST.get('linkers')
	grabNum = request.POST.get('grabNum')
	presses = request.POST.get('presses')
	tempDir = request.POST.get('temp')

	# head = request.META.items()
	# print 'header'
	# print head

	# session = request.session._get_or_create_session_key()
	# print 'in relative'
	# print session

	print 'in relative'
	key = request.session.session_key
	print key
	temp = request.session['temp']
	print temp

	for i in xrange(int(domains)):
		file = '%s/dom' %(tempDir) + str(i) + '.pdb'
		file = str(file)
		# log.info(file)
		# log.info(os.stat(file))
		# import pdb
		# pdb.set_trace()
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
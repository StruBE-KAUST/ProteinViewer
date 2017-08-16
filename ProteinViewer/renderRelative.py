import Biskit as B
from django.conf import settings
from .apps import VMDConfig
from .apps import MeshlabConfig
import json
from django.http import HttpResponse

import os
import subprocess
from subprocess import Popen, PIPE, STDOUT

def renderRelative(request):

	dompoints = []
	linkpoints = []
	domains = request.POST.get('domains')
	linkers = request.POST.get('linkers')
	grabNum = request.POST.get('grabNum')

	for i in xrange(int(domains)):
		file = '%spieces/dom' %(settings.MEDIA_ROOT) + str(i) + '.pdb'
		domain = B.PDBModel(file)
		# center = domain.boxCenter()
		# dompoints.append(json.dumps(center))
		center = domain.center()*0.05
		dompoints.append(json.dumps(center.tolist()))

	for i in xrange(int(linkers)):
		file = '%spieces/link' %(settings.MEDIA_ROOT) + str(i) + '.' + str(grabNum) + '.pdb'
		linker = B.PDBModel(file)
		# center = linker.boxCenter()
		# linkpoints.append(json.dumps(center))
		center = linker.center()*0.05
		linkpoints.append(json.dumps(center.tolist()))

	json_array = json.dumps([dompoints, linkpoints])

	return HttpResponse(json_array, content_type="application/json")
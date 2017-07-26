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
	# use full pdb to find the center, not parts. Need to get the proper pdb..
	m1 = B.PDBModel('%s/input_fk_Cit_centered.pdb' %(settings.MEDIA_ROOT))
	refpoint = m1.center()

	# split pdb up here, for now just use splitted pdbs:
	d1 = B.PDBModel('%s/01_fk_cut.pdb' %(settings.MEDIA_ROOT))
	d2 = B.PDBModel('%s/02_cit_cut.pdb' %(settings.MEDIA_ROOT))
	d1point = d1.center()
	d2point = d2.center()

	d1toref = d1point*0.05 - refpoint*0.05;
	d2toref = d2point*0.05 - refpoint*0.05;

	# run each split pdb through vmd, for now just use objs:
	# send generated objs to aframe along with vector somehow, for now
	# just send vector:
	pointdict = []
	pointdict.append(json.dumps(d1toref.tolist()))
	pointdict.append(json.dumps(d2toref.tolist()))

	json_array = json.dumps(pointdict)
	return HttpResponse(json_array, content_type="application/json")
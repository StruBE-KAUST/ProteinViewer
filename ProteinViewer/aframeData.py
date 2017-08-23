import Biskit as B 
import json
from django.http import HttpResponse
from django.conf import settings
from django.shortcuts import render
import numpy as np

import os
import subprocess
from subprocess import Popen, PIPE, STDOUT

from .apps import VMDConfig
from .apps import MeshlabConfig

from getLinker import getLinker

def returnData(request):
	# saves new coordinates of the domains in aframe to pdb files

	# first, parse the incoming lists from strings back to lists
	domStr = request.POST.get('domRanges')
	allStr = request.POST.get('allRanges')
	sequence = request.POST.get('sequence')
	presses = request.POST.get('presses')

	domEls = map(int, domStr.split(','))
	domRanges = []
	domTemp = []
	for i in xrange(len(domEls)):
		if i % 2 == 0:
			domTemp.append(domEls[i])
		else:
			domTemp.append(domEls[i])
			domRanges.append(domTemp)
			domTemp = []

	allEls = map(int, allStr.split(','))
	allRanges = []
	allTemp = []
	for i in xrange(len(allEls)):
		if i % 2 == 0:
			allTemp.append(allEls[i])
		else:
			allTemp.append(allEls[i])
			allRanges.append(allTemp)
			allTemp = []

	domains = len(domRanges)
	matrices = []

	for i in xrange(domains):
		mat = request.POST.get('mat' + str(i))
		matrices.append(mat)

	for i in xrange(domains):
		a = matrices[i]
		a = a.split(',')

		dom = B.PDBModel('%spdb' %(settings.MEDIA_ROOT) + str(i) + '.pdb')
		center = dom.center()

		index = 0
		for j in xrange(len(a)):
			if j != 3 and j != 7 and j != 11:
				a[j] = float(a[j])
			else:
				a[j] = float(a[j])*20 + center[index]
				index = index + 1
 
		asubbed = []
		atemp = []
		
		for k in range(len(a)):
			atemp.append(a[k])
			if k==3 or k==7 or k==11 or k==15:
				asubbed.append(atemp)
				atemp = []


		a = np.array(asubbed)
		anumpy = np.ndarray(shape=(4,4), dtype=float, buffer=a)

		dom = B.PDBModel('%spdb' %(settings.MEDIA_ROOT) + str(i) + 'ori.pdb')
		dom = dom.centered()
		domTrans = dom.transform(anumpy)
		domTrans.writePdb('%spdb' %(settings.MEDIA_ROOT) + str(i) + '.pdb')

	grabNum = request.POST.get('grabNum')

	runPrograms = getLinker(domRanges, allRanges, False, grabNum, sequence)

	# if the domains have been moved too far away for ranch to create a pool
	if runPrograms == 0:
		json_output = json.dumps([presses, runPrograms])
		return HttpResponse(json_output, content_type="application/json")

	linkers = len(allRanges) - len(domRanges)
	domains = len(domRanges)

	json_array = json.dumps([presses, domains, linkers])

	return HttpResponse(json_array, content_type="application/json")
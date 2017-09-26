"""
Put the domains' new positions (after a user moved them) into pdb files for
use in ranch. 
"""

import Biskit as B 
import json
from django.http import HttpResponse
from django.conf import settings
from django.shortcuts import render
import numpy as np

import os
import subprocess
from subprocess import Popen, PIPE, STDOUT

from .apps import CalledAppsConfig

from getLinker import getLinker

from models import DbEntry
from django.http import HttpResponseForbidden



def strParser(inputStr):
	"""
	Parse json string into list of lists
	@param inputStr: the list of lists as a json string
	@type inputStr: string
	"""

	els = map(int, inputStr.split(','))
	ranges = []
	temp = []

	# parse domRanges
	for i in xrange(len(els)):
		if i % 2 == 0:
			temp.append(els[i])
		else:
			temp.append(els[i])
			ranges.append(temp)
			temp = []

	return ranges

def transformPdb(matrices, domains, tempDir):
	"""
	Convert each matrix string to a matrix, then use to transform the
	pdbs and save as new pdbs
	@param matrices: list of strings
	@type matrices: list
	@param domains: number of domains in the molecule
	@type domains: int
	@param tempDir: directory for the user
	@type tempDir: unicode
	"""
	for i in xrange(domains):
		a = matrices[i]
		a = a.split(',')
		dom = B.PDBModel('%s/pdb' %(tempDir) + str(i) + '.pdb')
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

		# use the matrice on the pdb files and save as new pdbs
		dom = B.PDBModel('%s/pdb' %(tempDir) + str(i) + 'ori.pdb')
		dom = dom.centered()
		domTrans = dom.transform(anumpy)
		domTrans.writePdb('%s/pdb' %(tempDir) + str(i) + '.pdb')


def returnData(request, form_id):
	"""
	saves new coordinates of the domains in aframe to pdb files
	@param form_id: the form id taken from the request url
	@param type: unicode
	"""

	# check if session matches user
	obj = DbEntry.objects.get(form_id = form_id)
	session = request.session.session_key

	origin = obj.sessionId
	
	if origin != session:
		return HttpResponseForbidden()

	# first, parse the incoming lists from json strings back to lists
	domStr = request.POST.get('domRanges')
	allStr = request.POST.get('allRanges')
	sequence = request.POST.get('sequence')
	presses = request.POST.get('presses')
	rep = request.POST.get('rep')
	tempDir = request.POST.get('temp')
	grabNum = request.POST.get('grabNum')

	domRanges = strParser(domStr)
	allRanges = strParser(allStr)

	domains = len(domRanges)
	matrices = []

	for i in xrange(domains):
		mat = request.POST.get('mat' + str(i))
		matrices.append(mat)

	transformPdb(matrices, domains, tempDir)


	# use getLinker to run ranch, pulchra etc. to get new linker
	runPrograms = getLinker(domRanges, allRanges, False, grabNum, sequence, rep, tempDir)

	if runPrograms == None:
		# the domains have been moved too far away for ranch to create a pool
		json_output = json.dumps([presses, grabNum, runPrograms])
		return HttpResponse(json_output, content_type="application/json")

	linkers = len(allRanges) - len(domRanges)
	domains = len(domRanges)

	json_array = json.dumps([presses, grabNum, domains, linkers])

	return HttpResponse(json_array, content_type="application/json")
"""
Put the domains' new positions (after a user moved them) into pdb files for
use in ranch. 
"""

import Biskit as B 
import json
from django.http import HttpResponse
from django.http import HttpResponseForbidden

import numpy as np
import os
from getLinker import getLinker

from models import ViewingSession
from models import Domain
from models import Linker

def transformPdbs(matrices, number_of_domains, temporary_directory):
	"""
	Convert each matrix string to a matrix, then use to transform the
	pdbs and save as new pdbs
	@param matrices: list of strings
	@type matrices: list
	@param number_of_domains: number of domains in the molecule
	@type number_of_domains: int
	@param temporary_directory: directory for the user
	@type temporary_directory: unicode
	"""
	for i in xrange(number_of_domains):
		matrix = matrices[i]
		matrix = map(float, matrix.split(','))
		domain = B.PDBModel('{}/pdb'.format(temporary_directory) + str(i) + '.pdb')
		center = domain.center()

		# turn the translation parts of the matrix to the right scale and add on
		# the initial position given by renderRelative
		matrix[3] = matrix[3]*20 + center[0]
		matrix[7] = matrix[7]*20 + center[0]
		matrix[11] = matrix[11]*20 + center[0]
	
		matrix_subbed = []
		matrix_temp = []
		
		for k in range(len(a)):
			matrix_temp.append(matrix[k])
			if k==3 or k==7 or k==11 or k==15:
				matrix_subbed.append(matrix_temp)
				matrix_temp = []


		matrix = np.array(asubbed)
		matrix_numpy = np.ndarray(shape=(4,4), dtype=float, buffer=matrix)

		# use the matrice on the pdb files and save as new pdbs
		domain = B.PDBModel('{}/pdb'.format(temporary_directory) + str(i) + 'ori.pdb')
		domain = domain.centered()
		domain_transformed = domain.transform(matrix_numpy)
		domain_transformed.writePdb('{}/pdb'.format(temporary_directory) + str(i) + '.pdb')


def returnData(request, form_id):
	"""
	saves new coordinates of the domains in aframe to pdb files
	@param request: the post request object
	@type: django request
	@param form_id: the form id taken from the request url
	@type form_id: unicode
	"""

	# check if session matches user
	current_viewing_session = ViewingSession.objects.get(form_id=form_id)
	session_id = request.session.session_key

	original_session_id = current_viewing_session.session_id
	
	if original_session_id != session_id:
		return HttpResponseForbidden()

	domain_residue_ranges = []
	linker_residue_ranges = []
	all_residue_ranges = []

	domains = Domain.objects.filter(viewing_session=current_viewing_session)
	for domain in domains:
		residue_range = [domain.first_residue_number, domain.last_residue_number]
		domain_residue_ranges.append(residue_range)

	linkers = Linker.objects.filter(viewing_session=current_viewing_session)
	for linker in linkers:
		residue_range = [linker.first_residue_number, linker.last_residue_number]
		linker_residue_ranges.append(residue_range)

	all_residue_ranges.extend(domain_residue_ranges)
	all_residue_ranges.extend(linker_residue_ranges)
	all_residue_ranges = sorted(all_residue_ranges)

	representation = current_viewing_session.representation
	temporary_directory = current_viewing_session.temporary_directory

	presses = request.POST.get('presses')
	grab_number = request.POST.get('grab_number')

	number_of_domains = current_viewing_session.number_of_domains
	number_of_linkers = current_viewing_session.number_of_linkers
	matrices = []

	for i in xrange(number_of_domains):
		matrix = request.POST.get('mat' + str(i))
		matrices.append(matrix)

	transformPdbs(matrices, number_of_domains, temporary_directory)

	# use getLinker to run ranch, pulchra etc. to get new linker
	run_programs = getLinker(domain_residue_ranges, all_residue_ranges, False, grab_number, representation, temporary_directory)
	json_array = json.dumps([presses, grab_number, run_programs])

	return HttpResponse(json_array, content_type="application/json")
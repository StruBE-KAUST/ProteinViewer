"""
Processes data from form, then calls getLinker to run ranch/pulchra/vmd etc
and returns the viewer page
"""

from models import ViewingSession
from models import Linker
from models import Domain
from models import Asset
from models import Entity
from models import Box
from models import Line
from models import DOMAIN
from models import LINKER
from models import FAILED_STATE
from models import SUCCESS_STATE
from models import NO_SHIFT
from models import SHIFT

from django.http import HttpResponseForbidden

import time
import Biskit as B
import re

from getLinker import getLinker

def findDomainRanges(number_of_domains, temporary_directory, sequence):
	"""
	Find the residue ranges for each domain using the pdb files and sequence
	by matching the sequence extracted from the pdb file to the given sequence
	@param number_of_domains: number of domains
	@type number_of_domains: int
	@param temporary_directory: directory where files are located
	@type temporary_directory: string
	@param sequence: the sequence for the file
	@type sequence: string

	@return domain_residue_ranges: the residue ranges for each domain
	@rtype domain_residue_ranges: list of lists
	"""

	domain_residue_ranges = []

	for i in xrange(int(number_of_domains)):
	    m = B.PDBModel('{}'.format(temporary_directory) + '/pdb' + str(i) + '.pdb')
	    m = m.compress(m.maskProtein())
	    s = m.sequence()

	    # use regex to match the pdb sequence to the given sequence
	    match = re.search(s, sequence)
	    domain_residues = match.span()
	    domain_residues = [domain_residues[0], domain_residues[1]]
	    domain_residue_ranges.append(domain_residues)

	return domain_residue_ranges

def findAllRanges(domain_residue_ranges, sequence):
	"""
	Use the domain ranges and the sequence to find the linkers' residue ranges
	by checking for residue ranges in the sequence that are not covered by domains
	@param domain_residue_ranges: the residue ranges for all domains
	@type domain_residue_ranges: list
	@param sequence: the sequence for the file
	@type sequence: string

	@return all_residue_ranges: residue ranges for all domains and linkers
	@rtype: list of lists
	"""

	prev = 0
	end = len(sequence)
	all_residue_ranges = []

	for i in xrange(len(domain_residue_ranges)):
	    domain_residues = domain_residue_ranges[i]
	    if domain_residues[0] == prev and prev == 0:
	    	# there is no leading linker
	        all_residue_ranges.append(domain_residues)
	        prev = domain_residues[1]
	    elif domain_residues[0] != prev and prev == 0:
	    	# there is a leading linker
	        linker_residues = [prev, domain_residues[0] + 1]
	        all_residue_ranges.append(linker_residues)
	        all_residue_ranges.append(domain_residues)
	        prev = domain_residues[1]
	    elif domain_residues[0] != prev:
	    	# there is a linker present between this and the previous domain
	        linker_residues = [prev - 1, domain_residues[0] + 1]
	        all_residue_ranges.append(linker_residues)
	        all_residue_ranges.append(domain_residues)
	        prev = domain_residues[1]
	    else:
	    	# there is no linker present between this and the previous domain; 
	    	# place "linker" for continuity
	        linker_residues = [domain_residues[0] - 1, domain_residues[0] + 1]
	        all_residue_ranges.append(linker_residues)
	        all_residue_ranges.append(domain_residues)
	        prev = domain_residues[1]

	if(all_residue_ranges[len(all_residue_ranges) - 1])[1] != end:
		# there is a trailing linker
	    linker_residues = [prev - 1, end]
	    all_residue_ranges.append(linker_residues)

	return all_residue_ranges


def getBoxDetails(domain_residue_ranges, linker_residue_ranges, all_residue_ranges, temporary_directory):
	"""
	Use the domain-linker pattern to determine which domains the boxes (which
	indicate the domain-linker boundary) will follow. There are 4 cases:
	Case #1: linker_residue_ranges[0] == all_residue_ranges[0] and linker_residue_ranges[len(linker_residue_ranges) - 1] == all_residue_ranges[len(all_residue_ranges) - 1]
			 (ie. there is a leading linker and a trailing linker)
	Case #2: linker_residue_ranges[0] == all_residue_ranges[0]
			 (ie. there is a leading linker but no trailing linker)
	Case #3: linker_residue_ranges[len(linker_residue_ranges) - 1] == all_residue_ranges[len(all_residue_ranges) - 1]
			 (ie. there is a trailing linker but no leading linker)
	Case #4: else
			 (there is no leading or training linker)

	@param domain_residue_ranges: the residue ranges for all domains
	@type domain_residue_ranges: list
	@param linker_residue_ranges: the residue ranges for all linkers
	@type linker_residue_ranges: list
	@param all_residue_ranges: the residue ranges for all domains and linkers
	@type all_residue_ranges: list
	@param temporary_directory: directory to get files from
	@type temporary_directory: string

	@return: dictionary containing information of a shift for starting linker, and a list of the x,y,z positions of all the boxes
	@rtype: dictionary
	"""

	# remove trailing linkers from linker_residue_ranges, keeping track of leading ones 
	shifted_for_linker = NO_SHIFT
	linker_ranges = list(linker_residue_ranges)

	if linker_ranges[0] == all_residue_ranges[0]:
	    linker_ranges.remove(linker_ranges[0])
	    shifted_for_linker = SHIFT
	if linker_ranges[len(linker_ranges) - 1] == all_residue_ranges[len(all_residue_ranges) - 1]:
	    linker_ranges.remove(linker_ranges[len(linker_ranges) - 1])

	start_positions = []
	end_positions = []

	number_of_domains = len(domain_residue_ranges)

	# get the position of the start and end residues of each domain
	for i in xrange(number_of_domains):
	    m = B.PDBModel("{}/dom".format(temporary_directory) + str(i) + '.pdb')
	    residue = domain_residue_ranges[i]
	    shift = residue[0]
	    extremes = [residue[0] - shift, residue[1] - shift - 1]
	    start = m.takeResidues([extremes[0]])
	    end = m.takeResidues([extremes[1]])
	    startXyz = start.getXyz()*0.05
	    first = startXyz[0].tolist()
	    endXyz = end.getXyz()*0.05
	    # endXyz[0] seems to be better even though endXyz[len(endXyz) - 1] is the actual end..
	    end = endXyz[len(endXyz) - 1].tolist()
	    if i != 0:
	        start_positions.append(first)
	    if i != number_of_domains - 1:
	        end_positions.append(end)


	domain_number = 0

	box_details = []

	for i in xrange(len(linker_ranges)*2):
	    if i % 2 == 0:
	        # if even, take end_position and link to domain number
	        box_details.append([end_positions[0], domain_number])
	        end_positions.remove(end_positions[0])
	    else:
	        # if odd, up the domain number, take start_position and link to num
	        domain_number = domain_number + 1
	        box_details.append([start_positions[0], domain_number])
	        start_positions.remove(start_positions[0])

	return {'shifted_for_linker': shifted_for_linker, 'box_details': box_details}

def createDomainsOrLinkers(type_of_piece, number_of_pieces, current_viewing_session):
	'''
	Creates count number of the piece of given type, either domains or linkers,
	and saves them to the database.
	@param type_of_piece: the type of "piece", either "dom" or "link" for domain or linker
	@type type_of_piece: string
	@param number_of_pieces: number of pieces of the given type to make
	@type number_of_pieces: int
	@param current_viewing_session: the viewing session being used
	@type current_viewing_session: ViewingSession
	'''

	# TODO: when hull colliders are used, remove physics properties on the domain
	# and put "follow" component instead. Place physics properties on the hull collider

	form_id = current_viewing_session.form_id

	for i in xrange(number_of_pieces):
		if type_of_piece == "dom":
			obj_name = type_of_piece + str(i) + '.obj'
			mtl_name = type_of_piece + str(i) + '.mtl'
		elif type_of_piece == "link":
			obj_name = type_of_piece + str(i) + '.0.obj'
			mtl_name = type_of_piece + str(i) + '.0.mtl'
		else:
			return

		obj_id = type_of_piece + "_model" + str(i)
		obj_src = "/media/{}/".format(form_id) + obj_name
		mtl_id = type_of_piece + "_mat" + str(i)
		mtl_src = "/media/{}/".format(form_id) + mtl_name 

		a = Asset(obj_id=obj_id, obj_src=obj_src, mat_id=mtl_id, mat_src=mtl_src, viewing_session=current_viewing_session)
		a.save()


		if type_of_piece == "dom":
			entity_id = type_of_piece + str(i)
			entity_obj = "#dom_model" + str(i)
			entity_mat = "#dom_mat" + str(i)
			entity_class = "domain"
			entity_mixin = "dymol"
		else:
			entity_id = type_of_piece + str(i)
			entity_obj = "#link_model" + str(i)
			entity_mat = "#link_mat" + str(i)
			entity_class = "linker"
			entity_mixin = "dylink"

		e = Entity(entity_id=entity_id, entity_obj=entity_obj, entity_mat=entity_mat, entity_class=entity_class, entity_mixin=entity_mixin, viewing_session=current_viewing_session)
		e.save()

def createBoxes(details, current_viewing_session):
	'''
	Create the box entities and save them to the database
	@param details: dictionary containing information of a shift for starting linker, 
	and a list of the x,y,z positions of all the boxes
	@type details: dictionary
	@param current_viewing_session: the viewing session being used
	@type current_viewing_session: ViewingSession
	'''
	box_details = details['box_details']
	shifted_for_linker = details['shifted_for_linker']

	linker_number = 0
	for i in xrange(len(box_details)):
		if i % 2 != 0:
			linker_number = linker_number + 1

		box_id = "box" + str(i)
		box_position = str(box_details[i][0][0]) + ' ' + str(box_details[i][0][1]) + ' ' + str(box_details[i][0][2])
		box_target = "dom" + str(box_details[i][1])
		box_line = str(linker_number)
		box_link = str(linker_number + shifted_for_linker)

		b = Box(box_id=box_id, box_position=box_position, box_target=box_target, box_line=box_line, box_link=box_link, viewing_session=current_viewing_session)
		b.save()

def createLines(number_of_lines, current_viewing_session):
	'''
	Create lines to go between the boxes; there will always be an even number of boxes
	@param number_of_lines: the number of lines to be created
	@type number_of_lines: integer
	@param current_viewing_session: the viewing session being used
	@type current_viewing_session: ViewingSession
	'''
	for i in xrange(number_of_lines):
		line_id = "line" + str(i)
		line_start_box = "box" + str(i*2)
		line_end_box = "box" + str((i*2)+1)

		l = Line(line_id=line_id, line_start_box=line_start_box, line_end_box=line_end_box, viewing_session=current_viewing_session)
		l.save()


def load(form_id, session_id):
	"""
	Uses the user-entered values to get the residue ranges, calls getLinker, and saves resulting information in django models.
	@param form_id: the unique identifier for the form
	@type form_id: string
	@param session: the unique identifier for the user
	@type session: string
	"""

	# check if current user is the user that created the current ViewingSession
	current_viewing_session = ViewingSession.objects.get(form_id=form_id)

	original_session_id = current_viewing_session.session_id
	
	if original_session_id != session_id:
		return HttpResponseForbidden()

	number_of_domains = current_viewing_session.number_of_domains
	representation = current_viewing_session.representation.encode('ascii')
	sequence = current_viewing_session.sequence.encode('ascii')
	temporary_directory = current_viewing_session.temporary_directory.encode('ascii')

	start_time = time.time()
	domain_residue_ranges = findDomainRanges(number_of_domains, temporary_directory, sequence)
	all_residue_ranges = findAllRanges(domain_residue_ranges, sequence)

	counts = getLinker(domain_residue_ranges, all_residue_ranges, True, 0, representation, temporary_directory)
	
	if counts == FAILED_STATE: 
		# ranch was killed; domains too far apart
	    current_viewing_session.process_status = FAILED_STATE
	    current_viewing_session.save()
	    return

	number_of_domains = counts[0]
	number_of_linkers = counts[1]

	if number_of_domains != current_viewing_session.number_of_domains:
		# something went wrong, lost information
		current_viewing_session.process_status = FAILED_STATE
		current_viewing_session.save()
		return

	# use domain_residue_ranges and all_residue_ranges to sort for linkers' residue ranges
	linker_residue_ranges = []

	for i in all_residue_ranges:
	    if i in domain_residue_ranges:
	        pass
	    else: 
	        linker_residue_ranges.append(i)

	details = getBoxDetails(domain_residue_ranges, linker_residue_ranges, all_residue_ranges, temporary_directory)
	shifted_for_linker = details['shifted_for_linker']
	box_details = details['box_details']
	# lines span the gab between two boxes, connecting domains
	# there is always an even number of boxes
	number_of_lines = len(box_details)/2

	# TODO: Add hulls assets and entities when meshlab is up and running
	# don't give the hulls an mtl file and use the material property instead
	# to be able to set transparency and opacity (make invisible!) --> problem:
	# if hulls are produced as .dae models (why is this better?), cannot assign our own material

	# create the domain assets and entities
	createDomainsOrLinkers(DOMAIN, number_of_domains, current_viewing_session)
	createDomainsOrLinkers(LINKER, number_of_linkers, current_viewing_session)
	createBoxes(details, current_viewing_session)
	createLines(number_of_lines, current_viewing_session)

	end_time = time.time()

	time_taken = end_time - start_time
	print 'Whole process takes ' + str(time_taken) + ' to run'

	for dom in domain_residue_ranges:
		newDomain = Domain(first_residue_number=dom[0], last_residue_number=dom[1], viewing_session=current_viewing_session)
		newDomain.save()

	for link in linker_residue_ranges:
		newLinker = Linker(first_residue_number=link[0], last_residue_number=link[1], viewing_session=current_viewing_session)
		newLinker.save()

	current_viewing_session.process_status = SUCCESS_STATE
	current_viewing_session.shifted_for_linker = shifted_for_linker
	current_viewing_session.number_of_linkers = number_of_linkers
	current_viewing_session.number_of_lines = number_of_lines
	current_viewing_session.save()

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

import time
import Biskit as B

from getLinker import getLinker
from decorator import checkSession

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

@checkSession
def load(form_id, session_id):
	"""
	Uses the user-entered values to get the residue ranges, calls getLinker, and saves resulting information in django models.
	@param form_id: the unique identifier for the form
	@type form_id: string
	@param session: the unique identifier for the user
	@type session: string
	"""

	current_viewing_session = ViewingSession.objects.get(form_id=form_id)

	representation = current_viewing_session.representation
	sequence = current_viewing_session.sequence
	temporary_directory = current_viewing_session.temporary_directory

	start_time = time.time()
	domain_residue_ranges = current_viewing_session.createDomains()
	linker_residue_ranges = current_viewing_session.createLinkers(domain_residue_ranges)

	# use domain_residue_ranges and linker_residue_ranges to get all_residue_ranges
	all_residue_ranges = domain_residue_ranges + linker_residue_ranges
	all_residue_ranges = sorted(all_residue_ranges)

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

	details = getBoxDetails(domain_residue_ranges, linker_residue_ranges, all_residue_ranges, temporary_directory)
	shifted_for_linker = details['shifted_for_linker']
	box_details = details['box_details']
	# lines span the gab between two boxes, connecting domains
	# there is always an even number of boxes
	number_of_lines = len(box_details)/2

	current_viewing_session.shifted_for_linker = shifted_for_linker
	current_viewing_session.number_of_linkers = number_of_linkers
	current_viewing_session.number_of_lines = number_of_lines
	current_viewing_session.save()

	# TODO: Add hulls assets and entities when meshlab is up and running
	# don't give the hulls an mtl file and use the material property instead
	# to be able to set transparency and opacity (make invisible!) --> problem:
	# if hulls are produced as .dae models (why is this better?), cannot assign our own material

	# create the domain assets and entities
	current_viewing_session.createEntities(DOMAIN)
	current_viewing_session.createEntities(LINKER)
	current_viewing_session.createBoxes(details)
	current_viewing_session.createLines()

	end_time = time.time()

	time_taken = end_time - start_time
	print 'Whole process takes ' + str(time_taken) + ' to run'

	current_viewing_session.process_status = SUCCESS_STATE
	current_viewing_session.save()

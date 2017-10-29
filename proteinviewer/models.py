from django.db import models
from django.utils import timezone
from django.contrib import messages
from .apps import ProteinViewerConfig
import Biskit as B
import re


SUCCESS_STATE = 1
RUNNING_STATE = 0
FAILED_STATE = -1

SHIFT = 1
NO_SHIFT = 0

DOMAIN = "dom"
LINKER = "link"
HULL = "hull"

EMPTY = []


# Create your models here.

class ViewingSession(models.Model):
	form_id = models.CharField(max_length=100, unique=True)
	session_id = models.CharField(max_length=100, default='')
	date_created = models.DateTimeField(auto_now_add=True)
	temporary_directory = models.CharField(max_length=1000)
	number_of_domains = models.IntegerField(default=0)
	# TODO: find a way to differentiate between null and 0 linkers
	number_of_linkers = models.IntegerField(default=0)
	representation = models.CharField(max_length=100, default='')
	sequence = models.CharField(max_length=100000, default='')
	number_of_lines = models.IntegerField(default=0)
	shifted_for_linker = models.IntegerField(default=0)
	error_message = models.CharField(max_length=1000, default='')

	# fields for the loading process:
	process_status = models.IntegerField(default=RUNNING_STATE)

	def createDomains(self):
		"""
		Find the residue ranges for each domain using the pdb files and sequence
		by matching the sequence extracted from the pdb file to the given sequence
		@param self: the current viewing session object
		@type self: ViewingSession

		@return domain_residue_ranges: the residue ranges for each domain
		@rtype domain_residue_ranges: list of lists
		"""

		number_of_domains = self.number_of_domains
		temporary_directory = self.temporary_directory
		sequence = self.sequence

		if number_of_domains == 0:
			print 'no domains!'
			return EMPTY

		domain_residue_ranges = []

		for i in xrange(int(number_of_domains)):
		    m = B.PDBModel('{}'.format(temporary_directory) + '/pdb' + str(i) + '.pdb')
		    # supposed to clean..?:
		    m = m.compress(m.maskProtein())
		    s = m.sequence()
		    print s

		    # use regex to match the pdb sequence to the given sequence
		    match = re.search(s, sequence)
		    if match == None:
		    	# if ANY of the "domains" given by the user don't match, produce error
		    	print 'Pdbs do not match sequence'
		    	return EMPTY
		    domain_residues = match.span()
		    domain_residues = [domain_residues[0], domain_residues[1]]
		    domain_residue_ranges.append(domain_residues)

		for dom in domain_residue_ranges:
			newDomain = Domain(first_residue_number=dom[0], last_residue_number=dom[1], viewing_session=self)
			newDomain.save()

		return domain_residue_ranges


	def createLinkers(self, domain_residue_ranges):
		"""
		Use the domain ranges and the sequence to find the linkers' residue ranges
		by checking for residue ranges in the sequence that are not covered by domains
		@param self: the current viewing session
		@type self: ViewingSession
		@param domain_residue_ranges: the residue ranges for all domains
		@type domain_residue_ranges: list

		@return linker_residue_ranges: residue ranges for all linkers
		@rtype: list of lists
		"""
		sequence = self.sequence

		prev = 0
		end = len(sequence)
		linker_residue_ranges = []

		if domain_residue_ranges == EMPTY:
			return EMPTY

		for i in xrange(len(domain_residue_ranges)):
		    domain_residues = domain_residue_ranges[i]
		    if domain_residues[0] == prev and prev == 0:
		    	# there is no leading linker
		        prev = domain_residues[1]
		    elif domain_residues[0] != prev and prev == 0:
		    	# there is a leading linker
		        linker_residues = [prev, domain_residues[0] + 1]
		        linker_residue_ranges.append(linker_residues)
		        prev = domain_residues[1]
		    elif domain_residues[0] != prev:
		    	# there is a linker present between this and the previous domain
		        linker_residues = [prev - 1, domain_residues[0] + 1]
		        linker_residue_ranges.append(linker_residues)
		        prev = domain_residues[1]
		    else:
		    	# there is no linker present between this and the previous domain; 
		    	# place "linker" for continuity
		        linker_residues = [domain_residues[0] - 1, domain_residues[0] + 1]
		        linker_residue_ranges.append(linker_residues)
		        prev = domain_residues[1]

		number_of_domains = self.number_of_domains
		last_domain_residue = domain_residue_ranges[number_of_domains - 1][1]

		if len(sequence) != last_domain_residue:
			linker_residues = [last_domain_residue - 1, len(sequence)]
			linker_residue_ranges.append(linker_residues)
			prev = len(sequence)

		num_linkers = len(linker_residue_ranges)

		if num_linkers == 0:
			print 'no linkers!'
			return EMPTY

		if linker_residue_ranges[num_linkers - 1][1] != end and domain_residue_ranges[number_of_domains - 1][1] != end:
			# there is a trailing linker
		    linker_residues = [prev - 1, end]
		    linker_residue_ranges.append(linker_residues)

		for link in linker_residue_ranges:
			newLinker = Linker(first_residue_number=link[0], last_residue_number=link[1], viewing_session=self)
			newLinker.save()

		return linker_residue_ranges

	def createLines(self):
		'''
		Create lines to go between the boxes; there will always be an even number of boxes
		'''
		number_of_lines = self.number_of_lines

		for i in xrange(number_of_lines):
			line_id = "line" + str(i)
			line_start_box = "box" + str(i*2)
			line_end_box = "box" + str((i*2)+1)

			l = Line(line_id=line_id, line_start_box=line_start_box, line_end_box=line_end_box, viewing_session=self)
			l.save()

	def createBoxes(self, details):
		'''
		Create the box entities and save them to the database
		@param details: dictionary containing information of a shift for starting linker, 
		and a list of the x,y,z positions of all the boxes
		@type details: dictionary
		'''
		box_details = details['box_details']
		shifted_for_linker = details['shifted_for_linker']

		linker_number = 0
		for i in xrange(len(box_details)):

			box_id = "box" + str(i)
			box_position = str(box_details[i][0][0]) + " " + str(box_details[i][0][1]) + " " + str(box_details[i][0][2])
			box_target = "dom" + str(box_details[i][1])
			box_line = str(linker_number)
			box_link = str(linker_number + shifted_for_linker)

			if i % 2 != 0:
				linker_number = linker_number + 1

			b = Box(box_id=box_id, box_position=box_position, box_target=box_target, box_line=box_line, box_link=box_link, viewing_session=self)
			b.save()

	def createEntities(self, type_of_piece):
		'''
		Creates count number of the piece of given type, either domains or linkers,
		and saves them to the database.
		@param type_of_piece: the type of "piece", either "dom" or "link" for domain or linker
		@type type_of_piece: string

		'''

		# TODO: when hull colliders are used, remove physics properties on the domain
		# and put "follow" component instead. Place physics properties on the hull collider

		form_id = self.form_id
		use_hulls = ProteinViewerConfig.use_meshlab

		if type_of_piece == DOMAIN:
			number_of_pieces = self.number_of_domains
		else:
			number_of_pieces = self.number_of_linkers

		for i in xrange(number_of_pieces):
			if type_of_piece == DOMAIN:
				obj_name = type_of_piece + str(i) + '.obj'
				mtl_name = type_of_piece + str(i) + '.mtl'
				if use_hulls:
					hull_obj_name = HULL + str(i) + '.obj'
					hull_mtl_name = ""
			elif type_of_piece == LINKER:
				obj_name = type_of_piece + str(i) + '.0.obj'
				mtl_name = type_of_piece + str(i) + '.0.mtl'
			else:
				return

			obj_id = type_of_piece + "_model" + str(i)
			obj_src = "/media/{}/".format(form_id) + obj_name
			mtl_id = type_of_piece + "_mat" + str(i)
			mtl_src = "/media/{}/".format(form_id) + mtl_name 

			if type_of_piece == DOMAIN:
				if use_hulls:
					hull_obj_id = HULL + "_model" + str(i)
					hull_obj_src = "/media/{}/".format(form_id) + hull_obj_name

					a = Asset(obj_id=hull_obj_id, obj_src=hull_obj_src, viewing_session=self)
					a.save()

				a = Asset(obj_id=obj_id, obj_src=obj_src, mat_id=mtl_id, mat_src=mtl_src, viewing_session=self)
				a.save()
			else:
				a = Asset(obj_id=obj_id, obj_src=obj_src, mat_id=mtl_id, mat_src=mtl_src, viewing_session=self)
				a.save()



			if type_of_piece == DOMAIN:
				entity_id = type_of_piece + str(i)
				entity_obj = "#dom_model" + str(i)
				entity_mat = "#dom_mat" + str(i)
				entity_class = "domain"
				if use_hulls:
					entity_mixin = "mol"
					entity_target = HULL + str(i)

					hull_entity_id = HULL + str(i)
					hull_entity_obj = "#hull_model" + str(i)
					hull_entity_class = "hull"
					hull_entity_mixin = "dyhull"

					e = Entity(entity_id=entity_id, entity_obj=entity_obj, entity_mat=entity_mat, entity_class=entity_class, entity_mixin=entity_mixin, entity_target=entity_target, viewing_session=self)
					e.save()
					e = Entity(entity_id=hull_entity_id, entity_obj=hull_entity_obj, entity_class=hull_entity_class, entity_mixin=hull_entity_mixin, viewing_session=self)
					e.save()
				else:
					entity_mixin = "dymol"

					e = Entity(entity_id=entity_id, entity_obj=entity_obj, entity_mat=entity_mat, entity_class=entity_class, entity_mixin=entity_mixin, viewing_session=self)
					e.save()
			else:
				entity_id = type_of_piece + str(i)
				entity_obj = "#link_model" + str(i)
				entity_mat = "#link_mat" + str(i)
				entity_class = "linker"
				entity_mixin = "dylink"

				e = Entity(entity_id=entity_id, entity_obj=entity_obj, entity_mat=entity_mat, entity_class=entity_class, entity_mixin=entity_mixin, viewing_session=self)
				e.save()





class Linker(models.Model):
	first_residue_number = models.IntegerField()
	last_residue_number = models.IntegerField()

	viewing_session = models.ForeignKey(ViewingSession)

class Domain(models.Model):
	first_residue_number = models.IntegerField()
	last_residue_number = models.IntegerField()

	viewing_session = models.ForeignKey(ViewingSession)

class Asset(models.Model):
	obj_id = models.CharField(max_length=100, default='')
	obj_src = models.CharField(max_length=1000, default='')
	mat_id = models.CharField(max_length=100, default='')
	mat_src = models.CharField(max_length=1000, default='')

	viewing_session = models.ForeignKey(ViewingSession)

class Entity(models.Model):
	entity_id = models.CharField(max_length=100, default='')
	entity_obj = models.CharField(max_length=100, default='')
	entity_mat = models.CharField(max_length=100, default='')
	entity_class = models.CharField(max_length=100, default='')
	entity_mixin = models.CharField(max_length=100, default='')
	entity_target = models.CharField(max_length=100, default='')

	viewing_session = models.ForeignKey(ViewingSession)

class Box(models.Model):
	box_id = models.CharField(max_length=100, default='')
	box_position = models.CharField(max_length=100, default='')
	box_target = models.CharField(max_length=100, default='')
	box_line = models.CharField(max_length=100, default='')
	box_link = models.CharField(max_length=100, default='')

	viewing_session = models.ForeignKey(ViewingSession)

class Line(models.Model):
	line_id = models.CharField(max_length=100, default='')
	line_start_box = models.CharField(max_length=100, default='')
	line_end_box = models.CharField(max_length=100, default='')

	viewing_session = models.ForeignKey(ViewingSession)









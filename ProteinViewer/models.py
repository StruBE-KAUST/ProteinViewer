from django.db import models
from django.utils import timezone

SUCCESS_STATE = 1
RUNNING_STATE = 0
FAILED_STATE = -1

SHIFT = 1
NO_SHIFT = 0

DOMAIN = "dom"
LINKER = "link"


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

	# fields for the loading process:
	process_status = models.IntegerField(default=RUNNING_STATE)

	# def checkSequence(self, all_residue_ranges):
	# 	'''
	# 	Given all the residue ranges, checks to make sure the given sequence is covered exactly
	# 	@param all_residue_ranges: a list of lists giving the residue ranges for all
	# 							the domains and linkers in the molecule
	# 	@type all_residue_ranges: list of lists
	# 	'''
	# 	sequence = self.sequence.encode('ascii')
	# 	last_residue = len(sequence) - 1

	# 	print last_residue

	# 	prev = 0

	#	# careful with the logic here, because we made linkers and domains overlap 
	# 	# by a residue.. need to somehow allow for the overlap but not miss a missing piece..
	# 	for residue_range in all_residue_ranges:
	# 		print residue_range
	# 		if residue_range[0] != prev:
	# 			return FAILED_STATE
	# 		prev = residue_range[1]

	# 	print prev

	# 	if prev != last_residue:
	# 		return FAILED_STATE

	# 	return SUCCESS_STATE


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









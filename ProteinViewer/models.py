from django.db import models

SUCCESS_STATE = 1
RUNNING_STATE = 0
FAILED_STATE = -1

SHIFT = 1
NO_SHIFT = 0


# Create your models here.
class ViewingSession(models.Model):
	form_id = models.CharField(max_length=100, unique=True)
	session_id = models.CharField(max_length=100, default='')
	temporary_directory = models.CharField(max_length=1000)
	number_of_domains = models.IntegerField(default=0)
	# TODO: find a way to differentiate between null and 0 linkers
	number_of_linkers = models.IntegerField(default=0)
	representation = models.CharField(max_length=100, default='')
	sequence = models.CharField(max_length=10000, default='')
	number_of_lines = models.IntegerField(default=0)
	shifted_for_linker = models.IntegerField(default=0)

	# fields to be removed when asset & entity creation moves to template
	asset_string = models.CharField(max_length=1000000, default='')
	entity_string = models.CharField(max_length=1000000, default='')

	# fields for the loading process:
	process_status = models.IntegerField(default=0)


class Linker(models.Model):
	first_residue_number = models.IntegerField()
	last_residue_number = models.IntegerField()

	# foreign key to hold viewing session because each linker can have one viewing session
	# (many to one)
	viewing_session = models.ForeignKey(ViewingSession)

class Domain(models.Model):
	first_residue_number = models.IntegerField()
	last_residue_number = models.IntegerField()

	# foreign key to hold viewing session because each linker can have one viewing session
	# (many to one)
	viewing_session = models.ForeignKey(ViewingSession)
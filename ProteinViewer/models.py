from django.db import models

# Create your models here.
class DbEntry(models.Model):
	sessionId = models.CharField(max_length=100, default='')
	form_id = models.CharField(max_length=100, default='')
	pdbs = models.IntegerField(default=0)
	rep = models.CharField(max_length=100, default='')
	sequence = models.CharField(max_length=1000000, default='')

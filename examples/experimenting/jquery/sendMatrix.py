import Biskit as B 
import json
from django.http import HttpResponse

def makeMatrix():
	# m1 = B.PDBModel('01_fk.pdb')
	# m2 = B.PDBModel('02_cit.pdb')

	# t = m1.transformation(m1)

	r = {'matrix': 1}

	json_mod = json.dumps(r)
	
	print(json_mod)

	return HttpResponse(json_mod, content_type="application/json")

makeMatrix()
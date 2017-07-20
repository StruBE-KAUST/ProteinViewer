import Biskit as B 
import json
from django.http import HttpResponse
from django.conf import settings

def makeMatrix(request):

	m1 = B.PDBModel('%s/01_fk.pdb' %(settings.MEDIA_ROOT))
	# m2 = B.PDBModel('02_cit.pdb')

	t = m1.transformation(m1)

	mat = t[0].tolist()
	vec = t[1].tolist()
	onelist = []

	for sublist in mat:
		for item in sublist:
			onelist.append(item)
		onelist.append(0)
	onelist = onelist + [0, 0, 0, 1]

	json_mat = json.dumps(onelist)
	json_vec = json.dumps(vec)

	mix = {'matrix': json_mat, 'vector': json_vec}
	together = json.dumps(mix)
	
	return HttpResponse(together, content_type="application/json")
import Biskit as B 
import json
from django.http import HttpResponse

def makeMatrix(request):
	m1 = B.PDBModel('/Users/zahidh/Desktop/A-Frame/protein-viewer/ProteinViewer/testmats/01_fk.pdb')
	# m2 = B.PDBModel('02_cit.pdb')

	t = m1.transformation(m1)

	a = t[0].tolist()
	b = t[1].tolist()

	json_mat = json.dumps(a)
	json_vec = json.dumps(b)

	mix = {'matrix': json_mat, 'vector': json_vec}
	together = json.dumps(mix)
	
	return HttpResponse(together, content_type="application/json")
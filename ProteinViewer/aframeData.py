import Biskit as B 
import json
from django.http import HttpResponse
from django.conf import settings
from django.shortcuts import render
import numpy as np

from prepare4modeller import prep
from model_fkcit import modeller

def returnData(request):
	a = request.POST['mat0']
	a = a.split(',')
	for i in range(len(a)):
		a[i] = float(a[i])

	asubbed = []
	atemp = []

	for i in range(len(a)):
		atemp.append(a[i])
		if i==3 or i==7 or i==11 or i==15:
			asubbed.append(atemp)
			atemp = []

	b = request.POST['mat1']
	b = b.split(',')
	for i in range(len(b)):
		b[i] = float(b[i])

	bsubbed = []
	btemp = []

	for i in range(len(b)):
		btemp.append(b[i])
		if i==3 or i==7 or i==11 or i==15:
			bsubbed.append(btemp)
			btemp = []

	d1 = B.PDBModel('%s/01_fk_cut.pdb' %(settings.MEDIA_ROOT))
	d2 = B.PDBModel('%s/02_cit_cut.pdb' %(settings.MEDIA_ROOT))

	a = np.array(asubbed)
	b = np.array(bsubbed)

	anumpy = np.ndarray(shape=(4,4), dtype=float, buffer=a)
	bnumpy = np.ndarray(shape=(4,4), dtype=float, buffer=b)

	d1t = d1.transform(anumpy)
	d2t = d2.transform(bnumpy)

	# needed to make cit match sequence:
	d2t = d2t.compress(d2t.maskProtein())
	d2t = d2t.take(range(23, 1833))

	d1t.writePdb('%s/01_fk_cut_trans.pdb' %(settings.MEDIA_ROOT))
	d2t.writePdb('%s/02_cit_cut_trans.pdb' %(settings.MEDIA_ROOT))

	# make call to modeller here to use the new pdbs.
	prep()
	modeller()

	return render(request, "ProteinViewer/viewer.html")
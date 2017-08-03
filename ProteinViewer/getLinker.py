from django.conf import settings

import os
import subprocess
from subprocess import Popen, PIPE, STDOUT

from .apps import VMDConfig
from .apps import MeshlabConfig

import Biskit as B

def getLinker(domRanges, sequence):	
	# TODO: maybe make two functions, one gets just the linker and the other
	# gets the whole molecule? IDK.

	# TODO: make it accept the list of pdbs (or # of pdbs) it has to work with and the sequence file.
	# also needs to know domain ranges for cutting after pulchra

	# In this function, we take the pdbs and the sequence and run it through 
	# ranch to get the pdb file including the linker information. Then, we will
	# run them through pulchra.

	# TODO: build input string for ranch depending on the number of domains!
	# use a for loop, maybe?
	ranchInput = '\n \n ' + sequence + ' \n ' + str(len(domRanges)) + ' \n '
	for i in xrange(len(domRanges)):
		ranchInput = ranchInput + 'pdb' + str(i) + '.pdb \n yes \n \n '
	ranchInput = ranchInput + '10 \n \n yes \n output \n \n no \n' 


	# for now use hard-coded version
	# ranchInput = '\n \n target.fasta \n ' + str(len(domRanges)) + ' \n ' + '01_fk_cut_trans.pdb \n yes \n \n ' + '02_cit_cut_trans.pdb \n yes \n \n ' + '10 \n \n yes \n output \n \n no \n'

	# runs ranch with pdbs and sequence file

	# TODO: end the subprocess (or let it run in the background) when one file
	# is generated -- listen for a file and then end process?
	# TODO: use os.chdir(path) instead of cd for ranch and 


	# ranch = subprocess.Popen('cd %s && ranch' %(settings.MEDIA_ROOT), shell=True, stdin=PIPE)
	# ranch.communicate(input=b'' + ranchInput)

	# TODO: terminate ranch when one file is created



	# pulchraInput = '/Applications/pulchra304/bin/pulchra /Users/zahidh/Desktop/A-Frame/StruBE-website/data/media/session' + session + '/output/00001eom.pdb'
	pulchraInput = '/Applications/pulchra304/bin/pulchra /Users/zahidh/Desktop/A-Frame/StruBE-website/data/media/output/00001eom.pdb'
	# runs pulchra with pdb from ranch
	# TODO: change string depending on session file. Try use %s instead of absolute path too
	pulchra = subprocess.Popen(pulchraInput, shell=True)

	# TODO: add pdb breaking step here. Use domain ranges to cut the pdb produced
	# by pulchra. Note: this file doesn't have chain info. Also has repeat residue
	# numbers. How to differentiate..? ALSO: need not only the domains but also
	# need to take() the linker part into its own pdb...?! HELP WITH CUTTING!!

	# get ranges for all pieces using the ranges for the domains
	prev = 0
	allRanges = []
	for i in xrange(len(domRanges)):
		dom = domRanges[i]
		if dom[0] != prev:
			tup = (prev, dom[0] - 1)
			allRanges.append(tup)
			allRanges.append(dom)
			prev = dom[1]
		else:
			allRanges.append(dom)
			prev = dom[1]

	print allRanges

	# cut the output pdb into all the pieces, naming the pieces by +1 to the name
	m = B.PDBModel('%soutput/00001eom.rebuilt.pdb' %(settings.MEDIA_ROOT))

	for i in xrange(len(allRanges)):
		indices = range(allRanges[i][0], allRanges[i][1])
		piece = m.takeResidues(indices)
		pdb_name = '%spieces/pdb' %(settings.MEDIA_ROOT) + str(i) + '.pdb'
		piece.writePdb(pdb_name)

	# TODO: build vmd string to that we can launch just one and make all the 
	# models. OR: run many VMDs in parallel? Do the same for meshlab later.. (but
	# want to make sure that meshlab always runs after vmd finished running.. maybe 
	# have a for loop to launch them per piece? And inside the "parallel" call we
	# have synchronous calls to vmd then meshlab)
	pdb_name = "output/00001eom.rebuilt.pdb"
	rep = "newcartoon"

	vmdpath = VMDConfig().vmdpath
	meshpath = MeshlabConfig().meshpath

    # runs vmd to turn pdbs into .objs
    # TODO: either move this process to a different command, or have a way
    # to specify whether we want to vmd render all domains and linker or just linker
	# vmd = subprocess.Popen('cd %s && ./startup.command -dispdev none' %(vmdpath), shell=True, stdin=PIPE)
	# vmd.communicate(input=b'\n axes location off \n mol new %s%s \n mol rep %s \n mol addrep 0 \n mol delrep 0 0 \n scale to 0.05 \n render Wavefront %smodels/%s \n quit \n' %(settings.MEDIA_ROOT, pdb_name, rep, settings.MEDIA_ROOT, obj_name))

	# subprocess.call('cd %s && ./meshlabserver -i %smodels/%s -o %smodels/%s -m vc fc vn -s LowerResolution.mlx' %(meshpath, settings.MEDIA_ROOT, obj_name, settings.MEDIA_ROOT, obj_name), shell=True)

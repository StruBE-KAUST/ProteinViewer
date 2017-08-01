from django.conf import settings

import os
import subprocess
from subprocess import Popen, PIPE, STDOUT

from .apps import VMDConfig
from .apps import MeshlabConfig


def getLinker():	
	# TODO: make it accept the list of pdbs (or # of pdbs) it has to work with and the sequence file.
	# also needs to know domain ranges for cutting after pulchra

	# In this function, we take the pdbs and the sequence and run it through 
	# ranch to get the pdb file including the linker information. Then, we will
	# run them through pulchra.

	# TODO: build input string for ranch depending on the number of domains!
	# use a for loop, maybe?

	# runs ranch with pdbs and sequence file
	# TODO: end the subprocess (or let it run in the background) when one file
	# is generated -- listen for a file and then end process?
	# TODO: use os.chdir(path) instead of cd for ranch and vmd
	ranch = subprocess.Popen('cd %s && ranch' %(settings.MEDIA_ROOT), shell=True, stdin=PIPE)
	ranch.communicate(input=b'\n \n target.fasta \n 2 \n 01_fk_cut_trans.pdb \n yes \n \n 02_cit_cut_trans.pdb \n yes \n \n 10 \n \n yes \n output \n \n no \n')

	# runs pulchra with pdb from ranch
	# TODO: change string depending on session file. Try use %s instead of absolute path too
	pulchra = subprocess.Popen('/Applications/pulchra304/bin/pulchra /Users/zahidh/Desktop/A-Frame/StruBE-website/data/media/output/00001eom.pdb', shell=True)

	# TODO: add pdb breaking step here. Use domain ranges to cut the pdb produced
	# by pulchra. Note: this file doesn't have chain info. Also has repeat residue
	# numbers. How to differentiate..? ALSO: need not only the domains but also
	# need to take() the linker part into its own pdb...?! HELP WITH CUTTING!!

	# TODO: build vmd string to that we can launch just one and make all the 
	# models. OR: run many VMDs in parallel? Do the same for meshlab later..
	pdb_name = "output/00001eom.rebuilt.pdb"
	obj_name = "pdb.obj"
	rep = "newcartoon"

	vmdpath = VMDConfig().vmdpath
	meshpath = MeshlabConfig().meshpath

    # runs vmd to turn pdbs into .objs
    # TODO: either move this process to a different command, or have a way
    # to specify whether we want to vmd render all domains and linker or just linker
	vmd = subprocess.Popen('cd %s && ./startup.command -dispdev none' %(vmdpath), shell=True, stdin=PIPE)
	vmd.communicate(input=b'\n axes location off \n mol new %s%s \n mol rep %s \n mol addrep 0 \n mol delrep 0 0 \n scale to 0.05 \n render Wavefront %smodels/%s \n quit \n' %(settings.MEDIA_ROOT, pdb_name, rep, settings.MEDIA_ROOT, obj_name))

	# subprocess.call('cd %s && ./meshlabserver -i %smodels/%s -o %smodels/%s -m vc fc vn -s LowerResolution.mlx' %(meshpath, settings.MEDIA_ROOT, obj_name, settings.MEDIA_ROOT, obj_name), shell=True)

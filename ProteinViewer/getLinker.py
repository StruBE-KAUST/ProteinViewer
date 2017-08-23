from django.conf import settings

import os
import subprocess
from subprocess import Popen, PIPE, STDOUT
import signal
import threading
from .apps import VMDConfig
from .apps import MeshlabConfig

from threading import _Timer


import Biskit as B
import time

def getLinker(domRanges, allRanges, new, grabNum, sequence):	
	rep = "newcartoon" # TODO: get rep from user

	# In this function, we take the pdbs and the sequence and run it through 
	# ranch and pulchra to get the pdb file including the linker information.
	# Then, we run these files through VMD (and meshlab) for rendering

	ranchInput = '\n \n ' + sequence + ' \n ' + str(len(domRanges)) + ' \n '
	for i in xrange(len(domRanges)):
		ranchInput = ranchInput + 'pdb' + str(i) + '.pdb \n yes \n \n '
	ranchInput = ranchInput + '10 \n \n yes \n output \n \n no \n' 

	# TODO: use os.chdir(path) instead of cd for ranch and 
	
	starttime = time.time()

	ranch = ""

	def runRanch(timer):
		print 'thread running'
		global ranch 
		ranch = subprocess.Popen('cd %s && ranch' %(settings.MEDIA_ROOT), shell=True, stdin=PIPE, stdout=PIPE, preexec_fn=os.setsid)
		ranch.stdin.write(ranchInput)

		while ranch.poll() == None:
			line = ranch.stdout.readline()
			if str(line).strip() == '[  1%]':
				print 'possible'
				timer.cancel()
				print 'cancelled timer'
			if str(line).strip() == '[ 10%]':
				os.killpg(os.getpgid(ranch.pid), signal.SIGTERM)
			print line

	def killRanch():
		global ranch
		print "Out of time"
		os.killpg(os.getpgid(ranch.pid), signal.SIGTERM)
		return True

	class CustomTimer(_Timer):
	    def __init__(self, interval, function, args=[], kwargs={}):
	        self._original_function = function
	        super(CustomTimer, self).__init__(
	            interval, self._do_execute, args, kwargs)

	    def _do_execute(self, *a, **kw):
	        self.result = self._original_function(*a, **kw)

	    def join(self):
	        super(CustomTimer, self).join()
	        if hasattr(self, 'result'):
	        	return self.result
	        else:
	        	return False

	timer = CustomTimer(5, killRanch)
	reader = threading.Thread(target=runRanch, args=[timer])
	readStart = time.time()
	timer.start()
	reader.start()

	# Wait until thread is done
	reader.join()
	ranchKilled = timer.join()

	print 'reader joined'
	print ranchKilled

	if ranchKilled == True:
		print 'returning 0'
		return 0

	endtime = time.time()

	ranchtime = endtime - starttime
	print 'Ranch takes ' + str(ranchtime) + ' to run'

	pulchraInput = '/Applications/pulchra304/bin/pulchra /Users/zahidh/Desktop/A-Frame/StruBE-website/data/media/output/00001eom.pdb'
	# runs pulchra with pdb from ranch
	# TODO: change string depending on session file
	pulchra = subprocess.Popen(pulchraInput, shell=True)
	pulchra.wait()

	# cut the output pdb into all the pieces, naming the pieces by +1 to the name
	m = B.PDBModel('%soutput/00001eom.rebuilt.pdb' %(settings.MEDIA_ROOT))
	if new == True:
		m = m.centered()

	domCount = 0
	linkCount = 0

	for i in xrange(len(allRanges)):
		indices = range(allRanges[i][0], allRanges[i][1])
		piece = m.takeResidues(indices)
		pdb_name = ""
		ori_name = ""
		if allRanges[i] in domRanges:
			pdb_name = '%spieces/dom' %(settings.MEDIA_ROOT) + str(domCount) + '.pdb'
			if new == True:
				dom_name = '%spdb' %(settings.MEDIA_ROOT) + str(domCount) + '.pdb'
				ori_name = '%spdb' %(settings.MEDIA_ROOT) + str(domCount) + 'ori.pdb'
				piece.writePdb(ori_name)
				piece.writePdb(dom_name)
			domCount = domCount + 1
		else:
			pdb_name = '%spieces/link' %(settings.MEDIA_ROOT) + str(linkCount) + '.' + str(grabNum) + '.pdb'
			linkCount = linkCount + 1

		print pdb_name
		piece.writePdb(pdb_name)
			

	# TODO: want to make sure that meshlab always runs after vmd finished running.. maybe 
	# have a for loop to launch them per piece? And inside the "parallel" call we
	# have synchronous calls to vmd then meshlab
	vmdpath = VMDConfig().vmdpath
	meshpath = MeshlabConfig().meshpath

    # runs vmd to turn pdbs into .objs
	
	if new == True:
		for i in xrange(domCount):
			pdb_name = 'dom' + str(i) + '.pdb'
			obj_name = 'dom' + str(i) + '.obj'
			vmd = subprocess.Popen('cd %s && ./startup.command -dispdev none' %(vmdpath), shell=True, stdin=PIPE)
			vmd.communicate(input=b'\n axes location off \n mol new %spieces/%s \n mol rep %s \n mol addrep 0 \n mol delrep 0 0 \n scale to 0.05 \n render Wavefront %smodels/%s \n quit \n' %(settings.MEDIA_ROOT, pdb_name, rep, settings.MEDIA_ROOT, obj_name))
			vmd.wait()

	for i in xrange(linkCount):
		pdb_name = 'link' + str(i) + '.' + str(grabNum) + '.pdb'
		obj_name = 'link' + str(i) + '.' + str(grabNum) + '.obj'
		vmd = subprocess.Popen('cd %s && ./startup.command -dispdev none' %(vmdpath), shell=True, stdin=PIPE)
		vmd.communicate(input=b'\n axes location off \n mol new %spieces/%s \n mol rep %s \n mol addrep 0 \n mol delrep 0 0 \n scale to 0.05 \n render Wavefront %smodels/%s \n quit \n' %(settings.MEDIA_ROOT, pdb_name, rep, settings.MEDIA_ROOT, obj_name))
		vmd.wait()


	# TODO: make everything work with meshlab; doesn't run on macos. Note, run meshlab
	# on everything for lower resolution, but only on domains for the hull colliders
	# subprocess.call('cd %s && ./meshlabserver -i %smodels/%s -o %smodels/%s -m vc fc vn -s LowerResolution.mlx' %(meshpath, settings.MEDIA_ROOT, obj_name, settings.MEDIA_ROOT, obj_name), shell=True)

	return [domCount, linkCount]


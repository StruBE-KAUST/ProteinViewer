"""
Run the given pdbs and sequence through ranch and pulchra to get a pdb file 
with the linker information. Then, break this pdb file into domain and linker
pieces and run them through VMD (and meshlab) for rendering
"""


from django.conf import settings

import os
import subprocess
from subprocess import Popen, PIPE, STDOUT
import signal
import threading
from .apps import CalledAppsConfig

from threading import _Timer

import Biskit as B
import time

def getLinker(domRanges, allRanges, new, grabNum, sequence, rep, tempDir):	
	"""
	@param domRanges: residue ranges for all domains
	@type domRanges: list of lists, [[a,b],[c,d],...]
	@param allRanges: residue ranges for all domains and linkers
	@type allRanges: list of lists, [[a,b], [c,d], ...]
	@param new: whether this function is being called upon form submission
	@type new: bool
	@param grabNum: the number of times the domains have been moved
	@type grabNum: int
	@param sequence: the molecule sequence given by user
	@type sequence: str
	@param rep: the representation chosen by user
	@type rep: str
	@param tempDir: the temporary directory where user's files are stored
	@type tempDir: str

	@return [domCount, linkCount]: a list holding the number of domains and linkers
	@rtype: list [int, int]
	"""

	# create input string for ranch
	ranchInput = '\n \n ' + sequence + ' \n ' + str(len(domRanges)) + ' \n '
	for i in xrange(len(domRanges)):
		ranchInput = ranchInput + 'pdb' + str(i) + '.pdb \n yes \n \n '
	ranchInput = ranchInput + '10 \n \n yes \n \n \n no \n' 

	# TODO: use os.chdir(path) instead of cd for ranch?

	starttime = time.time()

	ranch = ""

	def runRanch(timer):
		"""
		The function run in the thread, runs ranch.
		@param timer: a timer to kill the thread if configuration is not possible
		@type timer: CustomTimer
		"""
		global ranch 
		ranch = subprocess.Popen('cd %s && ranch' %(tempDir), shell=True, stdin=PIPE, stdout=PIPE, preexec_fn=os.setsid)
		ranch.stdin.write(ranchInput)

		while ranch.poll() == None:
			# keep running ranch until ranch is killed
			line = ranch.stdout.readline()
			if str(line).strip() == '[  1%]':
				# ranch can form a linker, so cancel the timer and wait
				print 'possible'
				timer.cancel()
				print 'cancelled timer'
			if str(line).strip() == '[ 10%]':
				# ranch has formed a complete pdb; we only need one, so kill ranch
				os.killpg(os.getpgid(ranch.pid), signal.SIGTERM)
			print line

	def killRanch():
		"""
		Kills ranch
		"""
		global ranch
		print "Out of time"
		os.killpg(os.getpgid(ranch.pid), signal.SIGTERM)
		return True

	class CustomTimer(_Timer):
		"""
		Customized timer to allow us to know if ranch was killed by the timer
		(ie. configuration is not possible).
		"""
		def __init__(self, interval, function, args=[], kwargs={}):
			        self._original_function = function
			        super(CustomTimer, self).__init__(
				        interval, self._do_execute, args, kwargs)

		def _do_execute(self, *a, **kw):
			self.result = self._original_function(*a, **kw)

		def join(self):
			super(CustomTimer, self).join()
			if hasattr(self, 'result'):
				# if it has a result, ranch was killed by the timer
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

	if ranchKilled == True:
		return None

	endtime = time.time()

	ranchtime = endtime - starttime
	print 'Ranch takes ' + str(ranchtime) + ' to run'

	pulchrapath = CalledAppsConfig().pulchrapath

	pulchraInput = ' %s/00001eom.pdb' %(tempDir)
	# runs pulchra with pdb from ranch
	pulchra = subprocess.Popen(pulchraInput, shell=True)
	pulchra.wait()

	m = B.PDBModel('%s %s/00001eom.rebuilt.pdb' %(pulchrapath, tempDir))
	if new == True:
		m = m.centered()

	domCount = 0
	linkCount = 0

	# cut the output pdb into all the pieces, naming the pieces by +1 to the name
	for i in xrange(len(allRanges)):
		indices = range(allRanges[i][0], allRanges[i][1])
		piece = m.takeResidues(indices)
		pdb_name = ""
		ori_name = ""
		if allRanges[i] in domRanges:
			# if we're dealing with a domain:
			pdb_name = '%s/dom' %(tempDir) + str(domCount) + '.pdb'
			if new == True:
				dom_name = '%s/pdb' %(tempDir) + str(domCount) + '.pdb'
				ori_name = '%s/pdb' %(tempDir) + str(domCount) + 'ori.pdb'
				piece.writePdb(ori_name)
				piece.writePdb(dom_name)
			domCount = domCount + 1
		else:
			# if we're dealing with a linker:
			pdb_name = '%s/link' %(tempDir) + str(linkCount) + '.' + str(grabNum) + '.pdb'
			linkCount = linkCount + 1

		print pdb_name
		piece.writePdb(pdb_name)
			
	vmdpath = CalledAppsConfig().vmdpath
	meshpath = CalledAppsConfig().meshpath

    # runs vmd to turn pdbs into .objs
	if new == True:
		# only if loading for the first time we need to re-create the domains
		for i in xrange(domCount):
			pdb_name = 'dom' + str(i) + '.pdb'
			obj_name = 'dom' + str(i) + '.obj'
			vmd = subprocess.Popen('cd %s' %(vmdpath), shell=True, stdin=PIPE)
			vmd.communicate(input=b'\n axes location off \n mol new %s/%s \n mol rep %s \n mol addrep 0 \n mol delrep 0 0 \n scale to 0.05 \n render Wavefront %s/%s \n quit \n' %(tempDir, pdb_name, rep, tempDir, obj_name))
			vmd.wait()

	for i in xrange(linkCount):
		pdb_name = 'link' + str(i) + '.' + str(grabNum) + '.pdb'
		obj_name = 'link' + str(i) + '.' + str(grabNum) + '.obj'
		vmd = subprocess.Popen('cd %s' %(vmdpath), shell=True, stdin=PIPE)
		vmd.communicate(input=b'\n axes location off \n mol new %s/%s \n mol rep %s \n mol addrep 0 \n mol delrep 0 0 \n scale to 0.05 \n render Wavefront %s/%s \n quit \n' %(tempDir, pdb_name, rep, tempDir, obj_name))
		vmd.wait()


	# TODO: make everything work with meshlab; doesn't run on macos. Note, run meshlab
	# on everything for lower resolution, but only on domains for the hull colliders
	# TODO: When we put in meshlab, we want to make sure that meshlab always runs after vmd finished running.. maybe 
	# have a for loop to launch them per piece? And inside the "parallel" call we
	# have synchronous calls to vmd then meshlab
	# subprocess.call('cd %s && ./meshlabserver -i %smodels/%s -o %smodels/%s -m vc fc vn -s LowerResolution.mlx' %(meshpath, settings.MEDIA_ROOT, obj_name, settings.MEDIA_ROOT, obj_name), shell=True)

	return [domCount, linkCount]


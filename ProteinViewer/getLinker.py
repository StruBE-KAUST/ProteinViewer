"""
Run the given pdbs and sequence through ranch and pulchra to get a pdb file 
with the linker information. Then, break this pdb file into domain and linker
pieces and run them through VMD (and meshlab) for rendering
"""

import os
import subprocess
from subprocess import Popen, PIPE, STDOUT
import signal
import threading
from .apps import CalledAppsConfig

from threading import _Timer

import Biskit as B
import time

from models import FAILED_STATE

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

class ranchRunner():
	'''
	Class for running ranch
	'''

	ranch = None
		
	def runRanch(self, domain_residue_ranges, timer, do_all, temporary_directory):
		"""
		The function runs in the thread, runs ranch.
		@param domain_residue_ranges: the residue ranges for all domains
		@type domain_residue_ranges: list of lists
		@param timer: a timer to kill the thread if configuration is not possible
		@type timer: CustomTimer
		@param do_all: whether or not it is the first time running ranch; don't fix domain positions if true
		@type do_all: boolean
		@param temporary_directory: the directory where the files are located
		@type temporary_directory: string
		""" 

		# create input string for ranch
		ranch_input = '\n \n sequence.fasta \n' + str(len(domain_residue_ranges)) + ' \n '
		
		# TODO: Change this string to NOT fix positions if do_all is true
		# doesn't work right now because domains can be rendered too close
		# to eachother and bounce away: will work with hull colliders
		# if do_all == True:
		# 	for i in xrange(len(domain_residue_ranges)):
		# 		ranch_input = ranch_input + 'pdb' + str(i) + '.pdb \n no \n \n '
		# 	ranch_input = ranch_input + '10 \n \n yes \n \n \n no \n' 
		# else:
		# 	for i in xrange(len(domain_residue_ranges)):
		# 		ranch_input = ranch_input + 'pdb' + str(i) + '.pdb \n yes \n \n '
		# 	ranch_input = ranch_input + '10 \n \n yes \n \n \n no \n' 

		for i in xrange(len(domain_residue_ranges)):
			ranch_input = ranch_input + 'pdb' + str(i) + '.pdb \n yes \n \n '
		ranch_input = ranch_input + '10 \n \n yes \n \n \n no \n' 

		print 'Ranch input: ' + ranch_input

		self.ranch = subprocess.Popen('cd {} && ranch'.format(temporary_directory), shell=True, stdin=PIPE, stdout=PIPE, preexec_fn=os.setsid)
		ranch = self.ranch
		ranch.stdin.write(ranch_input)

		while ranch.poll() == None:
			# keep running ranch until ranch is killed
			line = ranch.stdout.readline()
			line = str(line).strip()
			if line == '[  1%]':
				# ranch can form a linker, so cancel the timer and wait
				timer.cancel()
				print 'cancelled timer'
			if line == '[ 10%]':
				# ranch has formed a complete pdb; we only need one, so kill ranch
				os.killpg(os.getpgid(ranch.pid), signal.SIGTERM)
			self.last_string = line
			print line

	def killRanch(self):
		"""
		Kills ranch
		"""

		ranch = self.ranch
		print "Domains are too far apart"
		os.killpg(os.getpgid(ranch.pid), signal.SIGTERM)

		# ranch = self.ranch
		# if ranch:
		# 	print "Domains are too far apart"
		# 	os.killpg(os.getpgid(ranch.pid), signal.SIGTERM)
		# else:
		# 	print "Sequence doesn't match"

		return True

	def runPulchra(self, temporary_directory):
		'''
		Runs pulchra, which creates the output file in the temporary directory given
		@param temporary_directory: the temporary directory where the files are
		@type: temporary_directory: string
		'''
		pulchra_path = CalledAppsConfig().pulchra_path

		pulchra_input = '{} {}/00001eom.pdb'.format(pulchra_path, temporary_directory)
		# runs pulchra with pdb from ranch
		pulchra = subprocess.Popen(pulchra_input, shell=True)
		pulchra.wait()

	def cutPdb(self, all_residue_ranges, domain_residue_ranges, temporary_directory, version, do_all):
		'''
		Cut the pdb that pulchra output into its respective domain and linker pdbs
		@param all_residue_ranges: the list of residue ranges for all the domains and linkers
		@type all_residue_ranges: list of lists
		@param domain_residue_ranges: the list of all domains' residue ranges
		@type domain_residue_ranges: list of lists
		@param temporary_directory: the directory where the files are located
		@type temporary_directory: string
		@param version: the number of times the domains have been moved
		@type version: integer
		@param do_all: whether or not all domains and linkers should be processed
		@type do_all: boolean

		@return: the number of domains and the number of linkers
		@rtype: list
		'''
		print 'version'
		print version

		number_of_domains = 0
		number_of_linkers = 0

		m = B.PDBModel('{}/00001eom.rebuilt.pdb'.format(temporary_directory))
		if do_all == True:
			m = m.centered()

		# cut the output pdb into all the pieces, naming the pieces by +1 to the name
		for i in xrange(len(all_residue_ranges)):
			indices = range(all_residue_ranges[i][0], all_residue_ranges[i][1])
			piece = m.takeResidues(indices)
			pdb_name = ""
			ori_name = ""
			if all_residue_ranges[i] in domain_residue_ranges:
				# if we're dealing with a domain:
				pdb_name = '{}/dom'.format(temporary_directory) + str(number_of_domains) + '.pdb'
				if do_all == True:
					domain_name = '{}/pdb'.format(temporary_directory) + str(number_of_domains) + '.pdb'
					original_name = '{}/pdb'.format(temporary_directory) + str(number_of_domains) + 'ori.pdb'
					piece.writePdb(original_name)
					piece.writePdb(domain_name)
				number_of_domains = number_of_domains + 1
			else:
				# if we're dealing with a linker:
				pdb_name = '{}/link'.format(temporary_directory) + str(number_of_linkers) + '.' + str(version) + '.pdb'
				number_of_linkers = number_of_linkers + 1

			piece.writePdb(pdb_name)

		return [number_of_domains, number_of_linkers]

	def runVmd(self, number_of_domains, number_of_linkers, version, temporary_directory, representation, do_all):
		'''
		Runs VMD to go from pdbs to .obj and .mtl files
		@param number_of_domains: the number of domains to turn to .objs
		@type number_of_domains: int
		@param number_of_linkers: the number fo linkers to turn to .objs
		@type number_of_linkers: int
		@param version: the number of times the domains have been moved
		@type: version: int
		@param temporary_directory: the temporary directory where files are locates
		@type temporary_directory: string
		@param representation: the representation chosen by the user
		@type representation: string
		@param do_all: whether or not all domains and linkers should be processed
		@type do_all: boolean
		'''
		vmd_path = CalledAppsConfig().vmd_path

		if do_all == True:
			# only if loading for the first time we need to re-create the domains
			for i in xrange(number_of_domains):
				pdb_name = 'dom' + str(i) + '.pdb'
				obj_name = 'dom' + str(i) + '.obj'
				vmd = subprocess.Popen('cd {}'.format(vmd_path), shell=True, stdin=PIPE)
				vmd.communicate(input=b'\n axes location off \n mol new {}/{} \n mol rep {} \n mol addrep 0 \n mol delrep 0 0 \n scale to 0.05 \n render Wavefront {}/{} \n quit \n'.format(temporary_directory, pdb_name, representation, temporary_directory, obj_name))
				vmd.wait()

		for i in xrange(number_of_linkers):
			pdb_name = 'link' + str(i) + '.' + str(version) + '.pdb'
			obj_name = 'link' + str(i) + '.' + str(version) + '.obj'
			vmd = subprocess.Popen('cd {}'.format(vmd_path), shell=True, stdin=PIPE)
			vmd.communicate(input=b'\n axes location off \n mol new {}/{} \n mol rep {} \n mol addrep 0 \n mol delrep 0 0 \n scale to 0.05 \n render Wavefront {}/{} \n quit \n'.format(temporary_directory, pdb_name, representation, temporary_directory, obj_name))
			vmd.wait()

	def getLinker(self, domain_residue_ranges, all_residue_ranges, do_all, version, representation, temporary_directory):	
		"""
		Runs ranch, pulchra, vmd (and meshlab) to produce the files needed for viewing
		@param domain_residue_ranges: residue ranges for all domains
		@type domain_residue_ranges: list of lists, [[a,b],[c,d],...]
		@param all_residue_ranges: residue ranges for all domains and linkers
		@type all_residue_ranges: list of lists, [[a,b], [c,d], ...]
		@param do_all: whether this function is being called upon form submission
		@type do_all: bool
		@param version: the number of times the domains have been moved
		@type version: int
		@param representation: the representation chosen by user
		@type representation: str
		@param temporary_directory: the temporary directory where user's files are stored
		@type temporary_directory: str

		@return [number_of_domains, number_of_linkers]: a list holding the number of domains and linkers
		@rtype: list [int, int]
		"""

		start_time = time.time()

		# allow ranch 5 seconds to determine if configuration is valid
		timer = CustomTimer(3, self.killRanch)
		reader = threading.Thread(target=self.runRanch, args=[domain_residue_ranges, timer, do_all, temporary_directory])
		timer.start()
		reader.start()

		# Wait until thread is done
		reader.join()
		ranch_killed = timer.join()

		if ranch_killed == True:
			return FAILED_STATE

		end_time = time.time()

		ranch_time = end_time - start_time
		print 'Ranch takes ' + str(ranch_time) + ' to run'

		# import pdb
		# pdb.set_trace()

		self.runPulchra(temporary_directory)
		counts = self.cutPdb(all_residue_ranges, domain_residue_ranges, temporary_directory, version, do_all)

		number_of_domains = counts[0]
		number_of_linkers = counts[1]

		print 'Domains: ' + str(number_of_domains)
		print 'Linkers: ' + str(number_of_linkers)

		self.runVmd(number_of_domains, number_of_linkers, version, temporary_directory, representation, do_all)


		# TODO: make everything work with meshlab; doesn't run on macos. Note, run meshlab
		# on everything for lower resolution, but only on domains for the hull colliders. Hull colliders will 
		# be produced at .dae models
		# TODO: When we put in meshlab, we want to make sure that meshlab always runs after vmd finished running.. maybe 
		# have a for loop to launch them per piece? And inside the "parallel" call we
		# have synchronous calls to vmd then meshlab
		# meshlab_path = CalledAppsConfig().meshlab_path
		# subprocess.call('cd {} && ./meshlabserver -i {}models/{} -o {}models/{} -m vc fc vn -s LowerResolution.mlx'.format(meshpath, settings.MEDIA_ROOT, obj_name, settings.MEDIA_ROOT, obj_name), shell=True)

		return [number_of_domains, number_of_linkers]


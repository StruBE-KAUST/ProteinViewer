"""
Run the given pdbs and sequence through ranch and pulchra to get a pdb file 
with the linker information. Then, break this pdb file into domain and linker
pieces and run them through VMD (and meshlab) for rendering
"""

import os
import subprocess
import signal
import threading
from subprocess import Popen, PIPE, STDOUT
from django.apps import apps
from django.conf import settings
from models import ViewingSession


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

		if do_all:
			for i in xrange(len(domain_residue_ranges)):
				ranch_input = ranch_input + 'pdb' + str(i) + '.pdb \n no \n \n '
			ranch_input = ranch_input + '10 \n \n yes \n \n \n no \n' 
		else:
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

	def killRanch(self, current_viewing_session):
		"""
		Kills ranch
		@param current_viewing_session: the viewing session to attach the error message to
		@type current_viewing_session: ViewingSession
		"""
		# ranch = self.ranch
		# print "Domains are too far apart"
		# os.killpg(os.getpgid(ranch.pid), signal.SIGTERM)

		ranch = self.ranch

		if ranch.poll() == None:
			os.killpg(os.getpgid(ranch.pid), signal.SIGTERM)
			message = "Domains are too far apart, or overlapping. Please select appropriate files."
			current_viewing_session.error_message = message
			current_viewing_session.save()
		else:
			message = "Domains can't be aligned to sequence. Please select appropriate files."
			current_viewing_session.error_message = message
			current_viewing_session.save()

		return True

	def runPulchra(self, temporary_directory):
		'''
		Runs pulchra, which creates the output file in the temporary directory given
		@param temporary_directory: the temporary directory where the files are
		@type: temporary_directory: string
		'''
                env = os.environ.copy()
                env["PATH"] = apps.get_app_config('proteinviewer').paths \
                              + ":" + env["PATH"]
		pulchra_input = 'pulchra {}/00001eom.pdb'.format(temporary_directory)
                
		# runs pulchra with pdb from ranch
		pulchra = subprocess.Popen(pulchra_input, env=env, shell=True)
		pulchra.wait()
		exit_status = pulchra.returncode
		if exit_status != 0:
                        if exit_status == 127:
                                raise RuntimeError("pulchra not found")
                        raise RuntimeError("pulchra exited with non-zero status")

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

		print 'all residues'
		print all_residue_ranges

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
                env = os.environ.copy()
                env["PATH"] = apps.get_app_config('proteinviewer').paths \
                              + ":" + env["PATH"]

		if do_all == True:
			# only if loading for the first time we need to re-create the domains
			for i in xrange(number_of_domains):
				pdb_name = 'dom' + str(i) + '.pdb'
				obj_name = 'dom' + str(i) + '.obj'
				vmd = subprocess.Popen('vmd', shell=True, stdin=PIPE, env=env)
				vmd.communicate(input=b'\n axes location off \n mol new {}/{} \n mol rep {} \n mol addrep 0 \n mol delrep 0 0 \n scale to 0.05 \n render Wavefront {}/{} \n quit \n'.format(temporary_directory, pdb_name, representation, temporary_directory, obj_name))
				vmd.wait()
				exit_status = vmd.returncode
				if exit_status != 0:
                                        if exit_status == 127:
                                                raise RuntimeError("VMD not found")
					raise RuntimeError("VMD exited with a non-zero status")

		for i in xrange(number_of_linkers):
			pdb_name = 'link' + str(i) + '.' + str(version) + '.pdb'
			obj_name = 'link' + str(i) + '.' + str(version) + '.obj'
			vmd = subprocess.Popen('vmd', shell=True, stdin=PIPE, env=env)
			vmd.communicate(input=b'\n axes location off \n mol new {}/{} \n mol rep {} \n mol addrep 0 \n mol delrep 0 0 \n scale to 0.05 \n render Wavefront {}/{} \n quit \n'.format(temporary_directory, pdb_name, representation, temporary_directory, obj_name))
			vmd.wait()
			exit_status = vmd.returncode
			if exit_status != 0:
                                if exit_status == 127:
                                        raise RuntimeError("VMD not found")
				raise RuntimeError("VMD exited with a non-zero status")

	def runMeshlab(self, current_viewing_session):
		''' 
		Runs meshlab on every .obj to lower the resolution. Runs meshlab on domains to produce convex hulls for use as hull colliders
		@param current_viewing_session: the viewing session who's values to use
		@type current_viewing_session: ViewingSession
		'''

		number_of_domains = current_viewing_session.number_of_domains
		number_of_linkers = current_viewing_session.number_of_linkers

                env = os.environ.copy()
                env["PATH"] = apps.get_app_config('proteinviewer').paths \
                              + ":" + env["PATH"]
                
		for i in xrange(number_of_domains):
			obj_name = 'dom' + str(i) + '.obj'
			# TODO: (Note) Using .obj to be able to override the material and make transparent; if .obj is too laggy, use .dae (but I don't know how to make .dae transparent)
			hull_name = 'hull' + str(i) + '.obj'
			# Run meshlab to lower resolution
			exit_status = subprocess.call('meshlabserver -i {}models/{} -o {}models/{} -m vc fc vn -s LowerResolution.mlx'.format( settings.MEDIA_ROOT, obj_name, settings.MEDIA_ROOT, obj_name), shell=True, env=env)
			if exit_status != 0:
                                if exit_status == 127:
                                        raise RuntimeError("Meshlab not found")
                                raise RuntimeError("Meshlab exited with a non-zero status")
			# Run meshlab to create convex hulls
			exit_status = subprocess.call('meshlabserver -i {}models/{} -o {}models/{} -m vc fc vn -s ConvexHull.mlx'.format(settings.MEDIA_ROOT, obj_name, settings.MEDIA_ROOT, hull_name), shell=True, env=env)
			if exit_status != 0:
                                if exit_status == 127:
                                        raise RuntimeError("Meshlab not found")
                                raise RuntimeError("Meshlab exited with a non-zero status")

		for i in xrange(number_of_linkers):
			obj_name = 'link' + str(i) + '.obj'
			# run meshlab to lower resolution
			exit_status = subprocess.call('meshlabserver -i {}models/{} -o {}models/{} -m vc fc vn -s LowerResolution.mlx'.format(settings.MEDIA_ROOT, obj_name, settings.MEDIA_ROOT, obj_name), shell=True, env=env)
			if exit_status != 0:
                                if exit_status == 127:
                                        raise RuntimeError("Meshlab not found")
                                raise RuntimeError("Meshlab exited with a non-zero status")

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


		form_id = temporary_directory[len(settings.MEDIA_ROOT):len(temporary_directory)]
		current_viewing_session = ViewingSession.objects.get(form_id=form_id)

		if do_all == True:
			# loading for the first time, clean pdbs of any non-standard residue (pulchra cannot run with them in)
			number_of_domains = current_viewing_session.number_of_domains
			for i in xrange(number_of_domains):
				pdb_name = '{}/pdb'.format(temporary_directory) + str(i) + '.pdb'
				m = B.PDBModel(pdb_name)
				m = m.compress(m.maskProtein())
				m.writePdb(pdb_name)

		start_time = time.time()

		# allow ranch 5 seconds to determine if configuration is valid
		timer = CustomTimer(3, self.killRanch, kwargs={'current_viewing_session': current_viewing_session})
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

		pulchra = self.runPulchra(temporary_directory)
		if pulchra == FAILED_STATE:
			message = "Oops! Something went wrong."
			print "Pulchra failed"
			current_viewing_session.error_message = message
			current_viewing_session.save()

		counts = self.cutPdb(all_residue_ranges, domain_residue_ranges, temporary_directory, version, do_all)

		number_of_domains = counts[0]
		number_of_linkers = counts[1]

		print 'Domains: ' + str(number_of_domains)
		print 'Linkers: ' + str(number_of_linkers)

		vmd = self.runVmd(number_of_domains, number_of_linkers, version, temporary_directory, representation, do_all)
		if vmd == FAILED_STATE:
			message = "Oops! Something went wrong."
			print "Vmd failed"
			current_viewing_session.error_message = message
			current_viewing_session.save()

		use_meshlab = apps.get_app_config('proteinviewer').use_meshlab

		if use_meshlab == True:
			meshlab = self.runMeshlab(current_viewing_session)
			# TODO: find a way to get meshlab return code too! (using subprocess.call...)
			message = "Oops! Something went wrong."
			print "Meshlab failed"
			current_viewing_session.error_message = message
			current_viewing_session.save()

		return [number_of_domains, number_of_linkers]


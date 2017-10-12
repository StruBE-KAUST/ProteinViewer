''' 
This view acts as a filter, checking which of the final pages to show to the user;
if the subprocess running load.py for this view is complete and all the files
needed for the viewer.html are ready, it shows the user the viewer.html page. If
not, it loads a simple loading page
'''

from django.shortcuts import render
from models import ViewingSession
from models import Domain
from models import Linker
from models import Asset
from models import Entity
from models import Box
from models import Line
from django.http import HttpResponseForbidden
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.urls import reverse


from models import SUCCESS_STATE
from models import RUNNING_STATE
from models import FAILED_STATE
from decorator import checkSession

from views import SubmitPdbFileView

@checkSession
def page(request, form_id):
	"""
	If the files are ready, loads the viewer page, and if not, loads the loading page
	@param request: request object from views.py
	@type request: django request
	@param form_id: the unique id of the form submitted
	@type form_id: string

	@return: HttpResponseObject
	"""
	current_viewing_session = ViewingSession.objects.get(form_id=form_id)
	process_status = current_viewing_session.process_status

	if process_status == RUNNING_STATE:
		# the subprocess is still running, wait
		return render(request, 'ProteinViewer/mid.html')
	elif process_status == SUCCESS_STATE:
		# subprocess completed, .obj files ready to be used
		domain_residue_ranges = []
		linker_residue_ranges = []

		domains = Domain.objects.filter(viewing_session=current_viewing_session)
		for domain in domains:
			residue_range = [domain.first_residue_number, domain.last_residue_number]
			domain_residue_ranges.append(residue_range)

		linkers = Linker.objects.filter(viewing_session=current_viewing_session)
		for linker in linkers:
			residue_range = [linker.first_residue_number, linker.last_residue_number]
			linker_residue_ranges.append(residue_range)

		all_residue_ranges = domain_residue_ranges + linker_residue_ranges
		all_residue_ranges = sorted(all_residue_ranges)

		assets = Asset.objects.filter(viewing_session=current_viewing_session)
		entities = Entity.objects.filter(viewing_session=current_viewing_session)
		boxes = Box.objects.filter(viewing_session=current_viewing_session)
		lines = Line.objects.filter(viewing_session=current_viewing_session)

		context = {'assets': assets, 'entities': entities, 'boxes': boxes, 'lines': lines, 'domain_residue_ranges': domain_residue_ranges, 'all_residue_ranges': all_residue_ranges, 'shift': current_viewing_session.shifted_for_linker, 'representation': current_viewing_session.representation, 'temporary_directory': current_viewing_session.temporary_directory, 'form_id': str(form_id)}
		return render(request, 'ProteinViewer/viewer.html', context)
	else:
		# something failed (most likely Ranch: given domains are too far apart)
		# TODO: Go back to the form!!
		# return HttpResponseForbidden()
		messages.error(request, "Domain configuration is not possible. Please select appropriate files.")
		return HttpResponseRedirect(reverse('ProteinViewer:home'))

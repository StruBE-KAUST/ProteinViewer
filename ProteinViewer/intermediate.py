from django.shortcuts import render
from models import ViewingSession
from models import Domain
from models import Linker
from django.conf import settings
from ast import literal_eval
from django.http import HttpResponseForbidden
from django.http import HttpResponse

from models import SUCCESS_STATE
from models import RUNNING_STATE
from models import FAILED_STATE

def page(request, form_id):
	"""
	View responsible for producing the loading page
	@param request: request object from views.py
	@type request: django request
	@param form_id: the unique id of the form submitted
	@type form_id: string
	"""
	# check if session matches user
	obj = ViewingSession.objects.get(form_id = form_id)
	session = request.session.session_key

	origin = obj.session_id
	
	if origin != session:
		return HttpResponseForbidden()

	state = obj.process_status

	if state == RUNNING_STATE:
		return render(request, 'ProteinViewer/mid.html')
	elif state == SUCCESS_STATE:
		domRanges = []
		linkRanges = []
		allRanges = []

		domains = Domain.objects.filter(viewing_session=obj)

		for dom in domains:
			r = [dom.first_residue_number, dom.last_residue_number]
			domRanges.append(r)

		linkers = Linker.objects.filter(viewing_session=obj)

		for link in linkers:
			r = [link.first_residue_number, link.last_residue_number]
			linkRanges.append(r)

		allRanges.extend(domRanges)
		allRanges.extend(linkRanges)

		allRanges = sorted(allRanges)

		context = {'assets': obj.asset_string, 'entities': obj.entity_string, 'numDomains': obj.number_of_domains, 'numLinkers': obj.number_of_linkers, 'domRanges': domRanges, 'allRanges': allRanges, 'lines': obj.number_of_lines, 'shift': obj.shifted_for_linker, 'rep': obj.representation, 'temp': obj.temporary_directory, 'form_id': obj.form_id}
		return render(request, 'ProteinViewer/viewer.html', context)
	else:
		# TODO: Go back to the form!! Getting this means it failed!
		return HttpResponseForbidden()

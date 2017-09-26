from django.shortcuts import render
from models import DbEntry
from django.conf import settings
from ast import literal_eval


def page(request, form_id):
	"""
	View responsible for producing the loading page
	@param request: request object from views.py
	@type request: django request
	@param form_id: the unique id of the form submitted
	@type form_id: string
	"""
	# check if session matches user
	obj = DbEntry.objects.get(form_id = form_id)
	session = request.session.session_key

	origin = obj.sessionId
	
	if origin != session:
		return HttpResponseForbidden()

	return render(request, 'ProteinViewer/mid.html')
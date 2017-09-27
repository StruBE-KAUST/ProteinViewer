from models import ViewingSession
from django.http import HttpResponseForbidden
from django.http import HttpResponse


def check(request, form_id):
	"""
	TODO: DOCUMENT
	"""

	obj = ViewingSession.objects.get(form_id = form_id)
	session = request.session.session_key

	origin = obj.session_id

	if origin != session:
		return HttpResponseForbidden()

	result = obj.process_status

	return HttpResponse(result, content_type="text/plain")

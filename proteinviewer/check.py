'''
This view acts as a poll that checks the database for whether or not the subprocess
running load.py is complete.
'''


from models import ViewingSession
from django.http import HttpResponse
from decorator import checkSession

@checkSession
def check(request, form_id):
    """
    Checks if the subprocess running load for this form_id is complete by polling the database
    @param request: get request from mid.html
    @type request: django request
    @param form_id: the id from form submission
    @type form_id: string

    @return: HttpResponseObject
    """
    current_viewing_session = ViewingSession.objects.get(form_id=form_id)
    process_status = current_viewing_session.process_status

    return HttpResponse(process_status, content_type="text/plain")

from models import ViewingSession
from django.http import HttpResponseForbidden


def checkSession(function):
    # check if current user is the user that created the current ViewingSession

    def wrapper(*args, **kw):
        if len(args) == 1:
            request = args[0]
            session_id = request.session.session_key
            form_id = kw['form_id']
        else:
            form_id = args[0]
            session_id = args[1]

        current_viewing_session = ViewingSession.objects.get(form_id=form_id)
        original_session_id = current_viewing_session.session_id

        if original_session_id != session_id:
            # wrong person trying to access session_id!
            # TODO: Go back to the form!!
            return HttpResponseForbidden()

        return function(*args, **kw)

    return wrapper

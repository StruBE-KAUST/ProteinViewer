from django.shortcuts import render
from django.urls import reverse
from django.views.generic import View
from django.contrib import messages
from django.conf import settings
from django.http import HttpResponseRedirect

from .forms import SubmitViewerDataForm

import logging
import os
import subprocess
import tempfile

class SubmitPdbFileView(View):
    """Main view to render the form if GET or error in POST
    render the VR viewer if no error in POST."""

    @staticmethod
    def render_form(request, form=None):
        """Render form."""
        log = logging.getLogger(__name__)
        log.debug("Enter with args: " + str(request) + " ; " + str(form))

        if form is None:
            form = SubmitViewerDataForm()

        response_data = render(
                request,
                'ProteinViewer/submit.html',
                {
                    'form': form,
                })

        log.debug("Exit")
        return response_data

    def get(self, request):
        """Serve the form to submit a PDB file."""
        return self.render_form(request)

    def post(self, request):
        """Serve the viewer page if valid form, else serve the form."""
        log = logging.getLogger(__name__)
        log.debug("Enter with args: " + str(request))

        form = SubmitViewerDataForm(
                request.POST,
                request.FILES)

        if form.is_valid():
            log.debug("Valid form")

            try:
                response = self.generate_viewer_page(request, form)
            except Exception as e:
                log.error("Error when trying to generate viewer page")
                log.error(e, exc_info=True)
                response = self.render_form(request, form)
                messages.error(request, "An unexpected error occurred.")
        else:
            log.debug("Invalid form")
            messages.error(request, "Please check the form.")
            response = self.render_form(request, form)

        log.debug("Exit")
        return response





    def generate_viewer_page(self, request, form):
        """
        Saves data from form to the database and files, then redirects to loading page
        @param self: the view itself
        @type self: SubmitPdbFileView
        @param request: the post request with the files and sequence from the form
        @type request: django request object
        @param form: the form, which is a modelForm
        @type form: SubmitViewerDataForm

        @return: HttpResponseObject
        """

        if request.session.session_key == None:
            request.session.create()
            request.session.save()

        session_id = request.session.session_key

        representation = request.POST['representation']

        temporary_directory = tempfile.mkdtemp(prefix="user_", dir=settings.MEDIA_ROOT)
        form_id = temporary_directory[len(settings.MEDIA_ROOT):len(temporary_directory)]

        # PDB files are stored in the created temporary directory 

        for count, u_file in enumerate(request.FILES.getlist('pdb_files')):
            with open(os.path.join(temporary_directory, 'pdb' + str(count) + '.pdb'), 'wb+') as destination:
                for chunk in u_file:
                    destination.write(chunk)

        # TODO: parse the input to get just the sequence string.. cause they could
        # upload the whole fasta file including that top line with the >
        sequence = request.POST['sequence']

        if len(sequence) == 0:
            messages.error(request, "Please provide a sequence.")
            response = self.render_form(request, form)

        with open(os.path.join(temporary_directory, 'sequence.fasta'), 'wb+') as destination:
            for chunk in request.POST['sequence']:
                destination.write(chunk)

        number_of_domains = len(request.FILES.getlist('pdb_files'))

        post = form.save(commit=False)
        post.form_id = form_id.encode('ascii')
        post.session_id = session_id.encode('ascii')
        post.temporary_directory = temporary_directory.encode('ascii')
        post.number_of_domains = number_of_domains
        post.representation = representation.encode('ascii')
        post.sequence = sequence.encode('ascii').strip()
        post.save()

        subprocess.Popen('python manage.py loadview ' + form_id + ' ' + session_id, shell=True)

        return HttpResponseRedirect(reverse("ProteinViewer:intermediate", kwargs={'form_id': form_id}))

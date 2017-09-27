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
    count = 0


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
                log.error(e)
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
        Saves data from form to the database and files, then redirects to load
        """

        if request.session.session_key == None:
            request.session.create()
            request.session.save()

        session = request.session.session_key

        rep = request.POST['representation']

        temp_directory = tempfile.mkdtemp(prefix="user_", dir=settings.MEDIA_ROOT)
        form_id = temp_directory[len(settings.MEDIA_ROOT):len(temp_directory)]

        # PDB files are stored in the created temporary directory 

        for count, u_file in enumerate(request.FILES.getlist('pdb_files')):
            with open(os.path.join(temp_directory, 'pdb' + str(count) + '.pdb'), 'wb+') as destination:
                for chunk in u_file:
                    destination.write(chunk)

        # TODO: parse the input to get just the sequence string.. cause they could
        # upload the whole fasta file including that top line with the >
        sequence = request.POST['sequence']

        with open(os.path.join(temp_directory, 'sequence.fasta'), 'wb+') as destination:
            for chunk in request.POST['sequence']:
                destination.write(chunk)

        pdbs = len(request.FILES.getlist('pdb_files'))

        post = form.save(commit=False)
        post.form_id = form_id
        post.session_id = session
        post.number_of_domains = pdbs
        post.representation = rep
        post.sequence = sequence
        post.temporary_directory = temp_directory
        post.save()

        subprocess.Popen('python manage.py loadview ' + form_id + ' ' + session, shell=True)

        return HttpResponseRedirect(reverse("ProteinViewer:intermediate", kwargs={'form_id': form_id}))

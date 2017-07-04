from django.shortcuts import render
from django.views.generic import View
from django.contrib import messages
from django.conf import settings


from .forms import SubmitPdbFileForm

import logging
import os

class SubmitPdbFileView(View):
    """Main view to render the form if GET or error in POST
    render the VR viewer if no error in POST."""

    @staticmethod
    def render_form(request, form=None):
        """Render form."""
        log = logging.getLogger(__name__)
        log.debug("Enter with args: " + str(request) + " ; " + str(form))

        if form is None:
            form = SubmitPdbFileForm()

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

        form = SubmitPdbFileForm(
                request.POST,
                request.FILES)

        if form.is_valid():
            log.debug("Valid form")

            try:
                response = self.generate_viewer_page(request)
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

    def generate_viewer_page(self, request):
        with open(os.path.join(settings.MEDIA_ROOT, 'newpdb.pdb'), 'wb+') as destination:
            for chunk in request.FILES['pdb_file']:
                destination.write(chunk)

        # The file is available in request.FILE['pdb_file']
        # as file descriptor.
        # You can for example save it somewhere :
        # with open(dest_file, 'wb') as destination:
        #   for chunk in request.FILES['pdb_file']:
        #     destination.write(chunk)

        # When all the stuff is done, you can render the page with a specific
        # context.
        # ctx = {'obj_file_url': 'generated/obj/file.obj'}
        # return render(request, 'ProteinViewer/viewer.html', ctx)
        # You just need to tweak viewer.html to use the variables from ctx (see
        # django doc about template tags, and especially about static files)
        # You can store the generated files in django.conf.settings.STATIC_ROOT

        # Return static view as previously done
        response = render(
                request,
                'ProteinViewer/viewer.html')
        return response

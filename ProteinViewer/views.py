from django.shortcuts import render
from django.views.generic import View
from django.contrib import messages
from django.conf import settings
from .apps import VMDConfig
from .apps import MeshlabConfig


from .forms import SubmitPdbFileForm

import logging
import os
import subprocess
from subprocess import Popen, PIPE, STDOUT

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
        # find a way to change the name per 
        name = 'pdb'
        rep = 'surf'
        pdb_name = name + '.pdb'
        obj_name = name + '.obj'
        mtl_name = name + '.obj.mtl'
        vmdpath = VMDConfig().vmdpath
        meshpath = MeshlabConfig().meshpath

        with open(os.path.join(settings.MEDIA_ROOT, pdb_name), 'wb+') as destination:
            for chunk in request.FILES['pdb_file']:
                destination.write(chunk)

        # TODO: here, need to do the pdb centering and cutting, so that when we
        # open up vmd we can run all the domains through to get objs. Then run 
        # them all through meshlab too. ## too slooooooww..? Run many vmds and 
        # meshlabs in parallel?

        # runs vmd and converts pdb into obj file (if want dae, convert in meshlab)
        # vmd = subprocess.Popen('cd /d %s && vmd -dispdev none' %(vmdpath), shell=True, stdin=PIPE)
        vmd = subprocess.Popen('cd %s && ./startup.command -dispdev none' %(vmdpath), shell=True, stdin=PIPE)
        # vmd.communicate(input=b'mol new C:/Users/zahidh/Desktop/A-Frame/StruBE-website/data/media/%s \n mol rep %s \n mol addrep 0 \n mol delrep 0 0 \n render Wavefront C:/Users/zahidh/Desktop/A-Frame/StruBE-website/data/media/models/%s \n quit \n' %(pdb_name, rep, obj_name))
        vmd.communicate(input=b'\n axes location off \n mol new %s/%s \n mol rep %s \n mol addrep 0 \n mol delrep 0 0 \n scale to 0.05 \n render Wavefront %smodels/%s \n quit \n' %(settings.MEDIA_ROOT, pdb_name, rep, settings.MEDIA_ROOT, obj_name))

        # now we want to run meshlab on the newly generated file to lower the resolution
        # commented because meshlab doesn't run well on mac
        # subprocess.call('cd %s && ./meshlabserver -i %smodels/%s -o %smodels/%s -m vc fc vn -s LowerResolution.mlx' %(meshpath, settings.MEDIA_ROOT, obj_name, settings.MEDIA_ROOT, obj_name), shell=True)
        # subprocess.call('cd %s && ./meshlabserver -i %smodels/%s -o %smodels/%s -m vc fc vn -s LowerResolution.mlx' %(meshpath, settings.MEDIA_ROOT, obj_name, settings.MEDIA_ROOT, obj_name), shell=True)

        # send render request with context to the template
        context = {'obj_file': obj_name, 'mtl_file': mtl_name}
        return render(request, 'ProteinViewer/viewer.html', context)
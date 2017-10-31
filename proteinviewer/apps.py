import os
from django.apps import AppConfig


class ProteinViewerConfig(AppConfig):
    """Configuration of ProteinViewer application."""

    # pylint: disable=too-many-instance-attributes

    name = 'proteinviewer'
    verbose_name = 'ProteinViewer'

    def __init__(self, *args, **kwargs):
        """Create a new configuration."""
        super(ProteinViewerConfig, self).__init__(*args, **kwargs)

        # Days between creation of a session and removal of the associated files
        self.session_delay = None

        # Enable/disable creation of a better collision box
        self.use_meshlab = False

    def ready(self):
        """Populate the configuration with default values."""
        # TODO: Read from config.ini file
        self.session_delay = 7
        self.use_meshlab = False

        # Change HOME for Biskit usage
        os.environ["HOME"] = "/home/dunatotatos"

class CalledAppsConfig():
    # meshpath = 'C:/Program Files/VCG/MeshLab'
    mesh_path = '/Applications/\'meshlab.app\'/Contents/MacOS'
    # vmdpath = 'C:/Program Files (x86)/University of Illinois/VMD'
    vmd_path = '/Applications/\'VMD 1.9.3.app\'/Contents/MacOS && ./startup.command -dispdev none'
    # pulchrapath = (enter windows path here)
    pulchra_path = '/Applications/pulchra304/bin/pulchra'
    # ranchpath = (enter ranch windows path here)
    # ranchpath = '/Applications/ATSAS/bin && ranch' - don't use becuase we need to be in the tempDir to use files

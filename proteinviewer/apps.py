import os
import ConfigParser
import logging

from django.apps import AppConfig


class ProteinViewerConfig(AppConfig):
    """Configuration of ProteinViewer application."""

    # pylint: disable=too-many-instance-attributes

    name = 'proteinviewer'
    verbose_name = 'ProteinViewer'

    def __init__(self, *args, **kwargs):
        """Create a new configuration."""
        super(ProteinViewerConfig, self).__init__(*args, **kwargs)

        # Init attributes
        self.session_delay = None
        self.use_meshlab = None

    def ready(self):
        """Populate the configuration from config.ini."""
        log = logging.getLogger(__name__)
        
        base_dir = os.path.dirname(os.path.abspath(__file__))
        config = ConfigParser.ConfigParser()
        config_file = os.path.join(base_dir, "config.ini")
        res = config.read(config_file)

        if res == []:
            log.error("config.ini does not exist.")
            log.error("Use config.template to create your config.ini")
            raise IOError("config file does not exist")

        self.session_delay = int(config.get("DEFAULT", "keep_time"))
        self.use_meshlab = bool(config.get("DEFAULT", "meshlab"))

        # Change HOME for Biskit usage
        os.environ["HOME"] = config.get("PATHS", "home")

        # Add additional paths to PATH
        self.paths = config.get("PATHS", "path")

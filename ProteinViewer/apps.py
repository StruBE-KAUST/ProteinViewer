from django.apps import AppConfig


class ProteinviewerConfig(AppConfig):
    name = 'ProteinViewer'

class CalledAppsConfig():
    # meshpath = 'C:/Program Files/VCG/MeshLab'
    meshpath = '/Applications/\'meshlab.app\'/Contents/MacOS'
    # vmdpath = 'C:/Program Files (x86)/University of Illinois/VMD'
    vmdpath = '/Applications/\'VMD 1.9.3.app\'/Contents/MacOS && ./startup.command -dispdev none'
    # pulchrapath = (enter windows path here)
    pulchrapath = '/Applications/pulchra304/bin/pulchra'
    # ranchpath = (enter ranch windows path here)
    # ranchpath = '/Applications/ATSAS/bin && ranch' - don't use becuase we need to be in the tempDir to use files
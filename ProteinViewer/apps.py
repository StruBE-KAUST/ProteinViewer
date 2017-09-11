from django.apps import AppConfig


class ProteinviewerConfig(AppConfig):
    name = 'ProteinViewer'

class VMDConfig():
    # vmdpath = 'C:/Program Files (x86)/University of Illinois/VMD'
    vmdpath = '/Applications/\'VMD 1.9.3.app\'/Contents/MacOS'

class MeshlabConfig():
    # meshpath = 'C:/Program Files/VCG/MeshLab'
    meshpath = '/Applications/\'meshlab.app\'/Contents/MacOS'
from django.core.management.base import BaseCommand, CommandError
from ProteinViewer.models import ViewingSession
from ProteinViewer.load import load

# import additional classes/modules as needed
# from myapp.models import Book

class Command(BaseCommand):
    help = 'Runs the load script'

    def add_arguments(self, parser):
        parser.add_argument('form_id', nargs='+', type=str)
        parser.add_argument('session', nargs='+', type=str)

    def handle(self, *args, **options):
      form_id = options['form_id'][0]
      session = options['session'][0]
      load(form_id, session)
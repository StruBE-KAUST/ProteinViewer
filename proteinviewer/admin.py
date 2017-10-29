from django.contrib import admin
from models import ViewingSession
from models import Linker
from models import Domain

# Register your models here.
admin.site.register(ViewingSession)
admin.site.register(Linker)
admin.site.register(Domain)
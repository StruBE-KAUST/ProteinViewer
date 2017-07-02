from django.conf.urls import url
from .views import SubmitPdbFileView

urlpatterns = [
    url(r'^$', SubmitPdbFileView.as_view(), name="home"),
]

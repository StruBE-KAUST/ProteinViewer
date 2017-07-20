from django.conf.urls import url
from .views import SubmitPdbFileView
import sendMatrix

urlpatterns = [
    url(r'^$', SubmitPdbFileView.as_view(), name="home"),
    url(r'^matrix/$', sendMatrix.makeMatrix, name="matrix")
]

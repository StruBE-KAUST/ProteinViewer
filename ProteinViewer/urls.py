from django.conf.urls import url
from .views import SubmitPdbFileView
import aframeData
import renderRelative
import load

urlpatterns = [
    url(r'^$', SubmitPdbFileView.as_view(), name="home"),
    url(r'^(?P<form_id>\w+)/return/$', aframeData.returnData, name="return"),
    url(r'^(?P<form_id>\w+)/relative/$', renderRelative.renderRelative, name="render"),
    url(r'^(?P<form_id>user_\w+)/$', load.load, name="load") 
]

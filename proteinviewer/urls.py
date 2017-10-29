from django.conf.urls import url
from .views import SubmitPdbFileView
import aframeData
import renderRelative
import load
import intermediate
import check

urlpatterns = [
    url(r'^$', SubmitPdbFileView.as_view(), name="home"),
    url(r'^(?P<form_id>user_\w+)/$', intermediate.page, name="intermediate"),
    url(r'^(?P<form_id>\w+)/return/$', aframeData.returnData, name="return"),
    url(r'^(?P<form_id>\w+)/relative/$', renderRelative.renderRelative, name="render"),
    url(r'^(?P<form_id>\w+)/load/$', load.load, name="load"),
    url(r'^(?P<form_id>\w+)/check/$', check.check, name="check")
]

from django.conf.urls import url
from .views import SubmitPdbFileView
import aframeData
import renderRelative

urlpatterns = [
    url(r'^$', SubmitPdbFileView.as_view(), name="home"),
    url(r'^return/$', aframeData.returnData, name="return"),
    url(r'^relative/$', renderRelative.renderRelative, name="render")
]

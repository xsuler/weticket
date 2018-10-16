# -*- coding: utf-8 -*-
#
from django.conf.urls import url

from adminpage.views import *

__author__ = "Epsirom"


urlpatterns = [
    url(r'^login$', AdminLoginIn.as_view()),
    url(r'^logout$', AdminLoginOut.as_view()),
    url(r'^activity/list?$', ActivityList.as_view(), name="activity_list"),
    url(r'^activity/delete?$', ActivityDelete.as_view(), name="activity_delete"),
    url(r'^activity/detail?$', ActivityDetail.as_view(), name="activity_detail"),
    url(r'^activity/create?$', ActivityCreate.as_view(), name="activity_create"),
    url(r'^image/upload?$', ImageUpload.as_view(), name="image_upload"),
]

# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author PZcat created at 2019/8/3 18:14

from django.urls import path
from . import views

app_name = 'doc'

urlpatterns = [
     path('download/', views.doc_download, name="doc_download"),
     path('docs/', views.DocListView.as_view(), name='doc_list'),
     path('fdownload', views.DownloadView.as_view(), name='f_download'),
]

# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author PZcat created at 2019/8/3 17:57

from django.urls import path
from . import views

app_name  = 'course'

urlpatterns = [
    path('', views.IndexView.as_view(), name="course_index"),
    path('<int:course_id>/', views.CourseDetailView.as_view(), name='course_detail'),
]
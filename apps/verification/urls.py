# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author PZcat created at 2019/8/6 16:36

from django.urls import path, re_path

from . import views


app_name = 'verification'

urlpatterns = [
    path('image_code/', views.image_code_view, name='image_code'),
    re_path('username/(?P<username>\w{5,20})/', views.check_username_view, name="check_username"),    # 注意，整个正则不能有空格
    re_path('mobile/(?P<mobile>1[3-9]\d{9})/', views.check_mobile_view, name="check_mobile"),
    path('sms_code/', views.SmsCodeView.as_view(), name="sms_code"),
]
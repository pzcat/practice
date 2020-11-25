# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author PZcat created at 2019/8/3 23:19

from django.urls import path
from . import views

app_name = "user"

urlpatterns = [
    path('login/', views.LoginView.as_view(), name="login"),
    path('register/', views.RegisterView.as_view(), name='register'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
]
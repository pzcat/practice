# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author PZcat created at 2019/9/2 22:05

from django.template import Library
from django.shortcuts import reverse

register = Library()


@register.simple_tag()
def add_class(field, class_str):
    return field.as_widget(attrs={'class': class_str})


# 解决用户填错url导致整个应用挂掉不能访问的bug
@register.simple_tag()
def my_url(pattern, *args):
    try:
        url = reverse(pattern, *args)
    except Exception as e:
        url = reverse('myadmin:wait')
    return url
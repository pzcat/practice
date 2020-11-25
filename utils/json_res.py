# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author PZcat created at 2019/8/8 18:19
import datetime

from django.http import JsonResponse
from django.core.serializers.json import DjangoJSONEncoder

from .json_code import Code
from . import json_code


class MyJSONEncoder(DjangoJSONEncoder):
    def default(self, o):
        if isinstance(o, datetime.datetime):
            return o.astimezone().strftime('%Y-%m-%d %H:%M:%S')
        else:
            return super().default(o)


def json_response(errno=Code.OK, errmsg='', data=None, kwargs=None):       # kwargs 扩展其他参数
    json_dict = {
        'errno': errno,
        'errmsg': errmsg,
        'data': data
    }

    if kwargs and isinstance(kwargs, dict):
        json_dict.update(kwargs)

    return JsonResponse(json_dict, encoder=MyJSONEncoder)
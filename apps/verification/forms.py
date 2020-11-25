# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author PZcat created at 2019/8/10 11:37

from django import forms
from django.core.validators import RegexValidator
from django_redis import get_redis_connection

from user.models import User

# 创建手机号码正则校验器
mobile_validator = RegexValidator(r'^1[3-9]\d{9}$', '手机号码格式不正确')

class CheckImageForm(forms.Form):
    '''
    校验表单
    注意：字段名要和json中data的字段名一致
    '''
    # 重写__init__以接收额外的request参数
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request')
        super().__init__(*args, **kwargs)

    mobile = forms.CharField(max_length=11, min_length=11, validators=[mobile_validator,], error_messages={
        'max_length': '手机号位数不正确',
        'min_length': '手机号位数不正确',
        'required': '手机号不能为空',
    })
    captcha = forms.CharField(max_length=4, min_length=4, error_messages={
        'max_length': '图形验证码为4位',
        'min_length': '图形验证码为4位',
        'required': '图形验证码不能为空',
    })

    def clean(self):
        clean_data = super().clean()
        mobile = clean_data.get('mobile')
        captcha = clean_data.get('captcha')
        if mobile and captcha:
            # 1.校验图形验证码
            image_code = self.request.session.get('image_code')
            if not image_code:
                raise forms.ValidationError('图形验证码失效')
            if image_code.upper() != captcha.upper():
                raise forms.ValidationError('输入的图片验证码不匹配')
            # 2. 是否60秒以内发送过短信
            redis_conn = get_redis_connection(alias='verify_code')
            if redis_conn.get('sms_flag_{}'.format(mobile)):
                raise forms.ValidationError('获取短信验证码过于频繁')
            # 3.校验手机号码是否注册
            if User.objects.filter(mobile=mobile).exists():
                raise forms.ValidationError('手机号码已注册，请重新输入')
        return clean_data
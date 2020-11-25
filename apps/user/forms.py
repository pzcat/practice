# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author PZcat created at 2019/8/12 20:49
import re

from django import forms
from django_redis import get_redis_connection
from django.db.models import Q
from django.contrib.auth import login

from verification import constants
from .models import User
from verification.forms import mobile_validator


class RegisterForm(forms.Form):
    """
    用户注册表单
    """
    username = forms.CharField(label="用户名", max_length=20, min_length=5,
                               error_messages={
                                   'max_length': '用户名长度不能大于20',
                                   'min_length': '用户名长度不能小于5',
                                   'required': '用户名不能为空',
                               })
    password = forms.CharField(label="密码", max_length=20, min_length=6,
                               error_messages={
                                   'max_length': '密码长度不能大于20',
                                   'min_length': '密码长度不能小于于6',
                                   'required': '密码不能为空',
                               })
    password_repeat = forms.CharField(label="确认密码", max_length=20, min_length=6,
                               error_messages={
                                   'max_length': '密码长度不能大于20',
                                   'min_length': '密码长度不能小于6',
                                   'required': '密码不能为空',
                               })
    mobile = forms.CharField(label="手机号", max_length=11, min_length=11, validators=[mobile_validator, ],
                               error_messages={
                                   'max_length': '手机号码长度为11位',
                                   'min_length': '手机号码长度为11位',
                                   'required': '手机号码不能为空',
                               })
    sms_code = forms.CharField(label="短信验证码", max_length=constants.SMS_CODE_LENGTH, min_length=constants.SMS_CODE_LENGTH,
                               error_messages={
                                   'max_length': '短信验证码长度不正确',
                                   'min_length': '短信验证码长度不正确',
                                   'required': '短信验证码不能为空',
                               })

    def clean_username(self):
        """
        校验用户名是否已存在于数据库
        :return:
        """
        username = self.cleaned_data.get('username')   # 如果前面校验通过则返回校验通过的值
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError('用户名已存在')
        return username

    '''
    clean_fieldName方法是相互独立的，其中一个方法检验不通过，仍执行其他方法
    多字段联合校验最好使用clean方法，而不是使用clean_fieldName
    '''

    def clean_mobile(self):
        mobile = self.cleaned_data.get('mobile')
        if User.objects.filter(mobile=mobile).exists():
            raise forms.ValidationError('手机号已被注册')
        return mobile

    def clean(self):
        """
        联合校验：密码是否等于确认密码，校验短信验证码
        :return:
        """
        clean_data = super().clean()
        # 校验密码是否一致
        password = clean_data.get('password')
        password_repeat = clean_data.get('password_repeat')

        if password != password_repeat:
            raise forms.ValidationError('两次输入密码不一致')

        # 校验短信验证码
        sms_code = clean_data.get('sms_code')
        mobile = clean_data.get('mobile')

        redis_conn = get_redis_connection(alias='verify_code')
        real_code = redis_conn.get('sms_text_{}'.format(mobile))

        if (not real_code) or (real_code.decode('utf-8') != sms_code):
            raise forms.ValidationError('短信验证码错误')


class LoginForm(forms.Form):
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)

    account = forms.CharField(error_messages={'required': '账户不能为空'})      # label 渲染的时候才需要
    password = forms.CharField(max_length=20, min_length=6,
                               error_messages={
                                   'max_length': '密码长度不能大于20',
                                   'min_length': '密码长度不能小于于6',
                                   'required': '密码不能为空',
                               })
    remember = forms.BooleanField(required=False)

    def clean_account(self):
        """
        校验用户名
        :return:
        """
        account = self.cleaned_data.get('account')

        # if re.match(r'^1[3-9]\d{9}$', account):
        #     pass
        # else:
        #     if len(account) < 5 or len(account) > 20:
        #         raise forms.ValidationError('用户账户格式不正确')
        if not re.match(r'^1[3-9]\d{9}$', account) and (len(account) < 5 or len(account) > 20):   # 不是手机号，且不符合username格式
            raise forms.ValidationError('用户账户格式不正确')
        # 单字段校验一定要返回值，否则出现空值异常
        return account

    def clean(self):
        """
        校验用户名密码，实现登录逻辑
        :return:
        """
        cleaned_data = super().clean()

        account = cleaned_data.get('account')
        password = cleaned_data.get('password')
        remember = cleaned_data.get('remember')

        # 登录逻辑
        # 判断用户名密码是否匹配
        # 先找到用户
        # select * from tb_user where mobile=account or username=account
        user_queryset = User.objects.filter(Q(mobile=account) | Q(username=account))
        # 判断用户是否存在
        if user_queryset:
            user = user_queryset.first()
            # 注意：数据库里存的密码不是明文
            if user.check_password(password):      # 如果密码匹配
                # 判断是否免登录
                if remember:
                    # 免登录n天
                    self.request.session.set_expiry(constants.REMEMBER_EXPIRES)
                else:
                    # 关闭浏览器时清空
                    self.request.session.set_expiry(0)
                    # 登录，使用django内置功能
                login(self.request, user)
            else:
                raise forms.ValidationError('密码错误')

        else:
            raise forms.ValidationError('用户账户不存在')

        return cleaned_data
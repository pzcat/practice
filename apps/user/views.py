from django.shortcuts import render, redirect, reverse
from django.views import View
from django.contrib.auth import logout

from .forms import RegisterForm, LoginForm
from utils.json_code import Code
from utils.json_res import json_response
from .models import User


class LoginView(View):
    """
    登录视图
    url: /user/login
    """
    def get(self, request):
        return render(request, 'user/login.html')

    def post(self, request):
        # 1. 先校验
        form = LoginForm(request.POST, request=request)
        if form.is_valid():

            return json_response(errmsg='恭喜登录成功')
        else:
            # 将表单的报错信息进行拼接
            error_msg_list = []
            for item in form.errors.values():
                error_msg_list.append(item[0])
            error_msg_str = '/'.join(error_msg_list)
            return json_response(errno=Code.PARAMERR, errmsg=error_msg_str)


class RegisterView(View):
    """
    注册视图
    url: '/user/register/'
    """
    def get(self, request):
        return render(request, 'user/register.html')

    def post(self, request):
        # 1. 校验数据
        form = RegisterForm(request.POST)
        if form.is_valid():
            # 创建数据
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            mobile = form.cleaned_data.get('mobile')
            # 创建对象
            # User.objects.create(username=username, password=password, mobile=mobile)    # 这种方法会向数据库存入明文密码
            User.objects.create_user(username=username, password=password, mobile=mobile)     # django自带方法，给密码加密
            return json_response(errmsg="恭喜您，注册成功！")

        else:
            # 将表单的报错信息进行拼接
            error_msg_list = []
            for item in form.errors.values():
                error_msg_list.append(item[0])
            error_msg_str = '/'.join(error_msg_list)
            return json_response(errno=Code.PARAMERR, errmsg=error_msg_str)


# 防止跟内置函数logout重名
class LogoutView(View):
    def get(self, request):
        logout(request)
        return redirect(reverse('user:login'))

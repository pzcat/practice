import logging
import random

from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.views import View
from django_redis import get_redis_connection

from utils.captcha.captcha import captcha
from . import constants
from user.models import User
from utils.json_res import json_response
from utils.json_code import Code, error_map
from .forms import CheckImageForm
from utils.yuntongxun.sms import CCP

# 日志器
logger = logging.getLogger('django')                  # 获取定义好的日志器（settings里面设置好的）


def image_code_view(request):
    """
    生成验证码
    url: /image_code/
    """
    # 1. 生成一个验证码：随机生成字符串，生成图片
    text, image = captcha.generate_captcha()             # 用text接收验证码文本，image接收验证码图片

    # 2. 在后端保存验证码用于校验，保存在session中
    request.session['image_code'] = text        # 将验证码生成的文本保存在 image_code 变量中
    # 定义过期时间:可以在app中创建一个储存常量的py文件constance，在里面定义常量
    request.session.set_expiry(constants.IMAGE_CODE_EXPIRES)

    # 3. 记录一个日志
    logger.info('Image code:{}'.format(text))

    # 4. 返回验证码图片
    return HttpResponse(content=image, content_type='image/jpg')


def check_username_view(request, username):
    """
    校验用户名
    url: /user_name/(?P<username>\w{5,20})/
    :param request:
    :param username:
    :return:
    """
    # 去数据库查询，然后返回
    # data = {
    #     "errno": "0",
    #     "errmsg": "ok",
    #     "data": {
    #         "username": username,  # 查询到的用户名
    #         "count": User.objects.filter(username=username).count()  # 查询记录条数
    #     }
    # }
    data = {
        "username": username,
        "count": User.objects.filter(username=username).count()
    }

    # 返回json数据
    return JsonResponse(data=data)

def check_mobile_view(request, mobile):
    """
    校验手机号
    url: /mobile/(?P<mobile>1[3-9]\d{9})/
    :param request:
    :param mobile:
    :return:
    """
    # 去数据库查询，然后返回
    data = {
        "errno": "0",
        "errmsg": "ok",
        "data": {
            "mobile": mobile,  # 查询到的用户名
            "count": User.objects.filter(mobile=mobile).count()  # 查询记录条数
        }
    }
    # 返回json数据
    return JsonResponse(data)

class SmsCodeView(View):
    """
    发送短信验证码
    url: /sms_code/
    """
    def post(self, request):
        '''
        1. 校验手机号码
        2. 校验图形验证码
        3. 重新发送验证码时间间隔
        4. 保存短信验证码
        5. 保存发送记录
        :param request:
        :return:
        '''
        # 1.校验手机号
        # mobile = request.POST.get('mobile')
        # 需要先重载form的构造方法 , forms.py
        form = CheckImageForm(request.POST, request=request)

        if form.is_valid():
            # 获取手机号码
            mobile = form.cleaned_data.get('mobile')
            # 生成短信验证码
            sms_code = ''.join([random.choice('0123456789') for _ in range(constants.SMS_CODE_LENGTH)])
            # 发送短信验证码 调用接口
            logger.info('发送短信验证码正常[mobile: %s sms_code: %s' % (mobile, sms_code))
            # ccp = CCP()
            # try:
            #     res = ccp.send_template_sms(mobile, [sms_code, constants.SMS_CODE_EXPIRES], "1")
            #     if res == 0:
            #         logger.info('发送短信验证码[正常][mobile: %s sms_code: %s]' % (mobile, sms_code))
            #     else:
            #         logger.error('发送短信验证码[失败][mobile: %s sms_code: %s]' % (mobile, sms_code))
            #         return json_response(error=Code.SMSFAIL, errmsg=error_map[Code.SMSFAIL])
            # except Exception as e:
            #     logger.error(('发送短信验证码[异常][mobile: %s message: %s]' % (mobile, e)))
            #     return  json_response(errno=Code.SMSERROR, errmsg=error_map[Code.SMSERROR])

            # 保存发送记录, 不存在session中因为时限不一致（session中所有key值的时限是统一的）,应存到redis中
            # 创建短信验证码发送记录的key
            sms_flag_key = 'sms_flag_{}'.format(mobile)
            # 创建短信验证码内容的key
            sms_text_key = 'sms_text_{}'.format(mobile)

            # 创建连接
            redis_conn = get_redis_connection(alias='verify_code')
            # 创建管道
            pl = redis_conn.pipeline()

            try:
                pl.setex(sms_flag_key, constants.SMS_CODE_INTERVAL, 1)
                # 第一个参数:key名，第二个参数：过期时间,第三个参数：对应值
                pl.setex(sms_text_key, constants.SMS_CODE_EXPIRES*60, sms_code)
                # 让管道通知redis执行命令
                pl.execute()
                return json_response(errmsg='短信发送成功！')
            except Exception as e:
                logger.error('redis 执行异常：{}'.format(e))
                return json_response(errno=Code.UNKOWNERR, errmsg=error_map[Code.UNKOWNERR])

        else:
            # 将表单的报错信息进行拼接
            error_msg_list = []
            for item in form.errors.values():
                error_msg_list.append(item[0])
            error_msg_str = '/'.join(error_msg_list)
            return json_response(errno=Code.PARAMERR, errmsg=error_msg_str)

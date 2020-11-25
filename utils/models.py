# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author PZcat created at 2019/8/15 20:48

from django.db import models


class BaseModel(models.Model):
    """
    基类，公共字段，定义为抽象类，不在数据库里生成表
    """
    # auto_now_add 和 auto_now是django框架定义的
    create_time = models.DateTimeField('创建时间', auto_now_add=True)
    update_time = models.DateTimeField('更新时间', auto_now=True)
    is_deleted = models.BooleanField('逻辑删除', default=False)

    class Meta:
        # 声明该类为抽象类，用于继承，迁移的时候不创建
        abstract = True
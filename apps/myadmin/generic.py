# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author PZcat created at 2019/10/17 17:15
from django.core.exceptions import ImproperlyConfigured, ObjectDoesNotExist
from django.forms import modelform_factory
from django.http.request import QueryDict
from django.views import View
from django.shortcuts import render
from django.core.paginator import Paginator

from utils.json_res import json_response


class MyListView(View):
    model = None                  # 使用的模型
    template_name = None          # 模板名称
    is_paginated = False          # 是否分页
    per_page = None               # 每页条数
    page_header = None            # 页头大标题
    page_option = None            # 页头副标题
    table_title = None            # 内容标题

    fields = None                 # 要展示的字段

    def get(self, request):
        # 1. 获取模板变量
        context = self.get_context_data()
        # 2. 返回渲染的模板
        return render(request, self.get_template_name(), context=context)

    def get_template_name(self):
        """ 获取模板名称 """
        if self.template_name is None:
            self.template_name = 'myadmin/{0}/{0}_list.html'.format(self.model._meta.model_name)
            print(self.template_name)
        return self.template_name

    def get_context_data(self, **kwargs):
        """ 获取上下文变量，如果要添加额外变量，需要覆盖此方法 """
        # 1. 获取查询集
        queryset = self.get_queryset()

        # 2. 分页
        if self.is_paginated:                                         # 如果分页，返回pagination对象，否则返回queryset对象
            page_size = self.per_page
            if page_size:
                page = self.paginate_queryset(queryset, page_size)
            else:
                page = self.paginate_queryset(queryset, 10)
        else:
            page = queryset

        context = {
            'page': page,
            'page_header': self.page_header,
            'page_option': self.page_option,
            'table_title': self.table_title
        }
        context.update(kwargs)
        return context

    def get_queryset(self):
        """ 获取查询集，如果需要过滤，覆盖此方法 """
        # 1. 获取所有查询集
        if self.model is not None:
            queryset = self.model.objects.all()      # 或 queryset = self.model.objects.all()  self.model.default_manager
        else:
            raise ImproperlyConfigured(
                "%(cls)s 的model还没有指定啊亲" % {
                    'cls': self.__class__.__name__
                }
            )
        # 2. 选择字段
        if self.fields:
            queryset = queryset.only(*self.fields)
        return queryset

    def paginate_queryset(self, queryset, page_size):
        """ 分页方法 """
        paginator = Paginator(queryset, page_size)

        try:
            page_num = int(self.request.get('page', 1))
        except Exception as e:
            page_num = 1
        page = paginator.get_page(page_num)              # 返回当前页的pagenator对象
        return page


class MyUpdateView(View):
    model = None                  # 使用的模型
    form_class = None             # 模型表单类
    template_name = None          # 模板名称
    per_page = None               # 每页条数
    page_header = None            # 页头大标题
    page_option = None            # 页头副标题
    table_title = None            # 内容标题

    fields = None                 # 要展示的字段

    pk = None                     # url路径参数名，默认为pk

    def get(self, request, **kwargs):
        # 1. 获取对象
        self.obj = self.get_obj(**kwargs)
        # 2. 获取模板变量
        context = self.get_context_data()
        # 3. 返回渲染的模板
        return render(request, self.get_template_name(), context=context)

    def put(self, request, **kwargs):
        # 1. 获取模型对象
        self.obj = self.get_obj(**kwargs)
        # 2. 获取参数，创建模型表单对象
        self.form_class = self.get_form_class()
        form = self.form_class(QueryDict(request.body), instance=self.obj)
        # 3. 校验
        if form.is_valid():
            self.save(form)
            return json_response(errmsg='修改数据成功！')
        else:
            return render(request, self.get_template_name(), context=self.get_context_data(form=form))
        # 4. 返回结果

    def get_obj(self, **kwargs):
        """ 获取需要修改的对象 """
        # 1. 拿到主键
        self.get_obj_id(**kwargs)
        # 2. 根据模型获取对象
        if self.model is None:
            raise ImproperlyConfigured('没有设置模型')
        obj = self.model.objects.filter(pk=self.obj_id).first()
        if not obj:
            raise ObjectDoesNotExist('找不到pk=%s的对象' % self.obj_id)
        # 3. 返回

    def get_obj_id(self, **kwargs):
        """ 获取传递的主键 """
        if self.pk is None:
            self.obj_id = kwargs.get('pk')
        else:
            self.obj_id = kwargs.get(self.pk)

    def get_context_data(self, **kwargs):
        """ 获取上下文变量 """
        # 1. 获取表单类
        self.form_class = self.get_form_class()
        # 2. 创建表单对象
        form = self.form_class(instance=self.obj)
        # 3. 构造模板变量
        context = {
            'form': form,
            'page_header': self.page_header,
            'page_option': self.page_option,
            'table_title': self.table_title
        }
        context.update(kwargs)
        return context

    def get_form_class(self):
        """ 获取模型表单类 """
        if self.form_class is None:
            if self.fields is None:
                raise ImproperlyConfigured('既没有设置form，又没有设置fields字段，没法生成表单')
            return modelform_factory(self.model, fields=self.fields)
        else:
            return self.form_class

    def get_template_name(self):
        """ 获取模板名称 """
        if self.template_name is None:
            self.template_name = 'myadmin/{0}/{0}_detail.html'.format(self.model._meta.model_name)
            print(self.template_name)
        return self.template_name

    def save(self, form):
        """ 保存对象 """
        if form.has_changed():
            instance = form.save(commit=False)
            instance.save(update_fields=form.changed_data)         # 只更新有修改的对象

# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author PZcat created at 2019/9/2 18:36

from django import forms
from django.contrib.auth.models import Group
from ckeditor_uploader.widgets import CKEditorUploadingWidget

from .models import Menu, Permission
from user.models import User
from news.models import News, Tag


class MenuModelForm(forms.ModelForm):
    # 修改字段属性和初始化方法，使渲染时表单能区分父菜单
    parent = forms.ModelChoiceField(queryset=None, required=False, help_text='父菜单')    # 重写父菜单属性，渲染成单选框

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['parent'].queryset = Menu.objects.filter(is_deleted=False, is_visible=True, parent=None)


    class Meta:
        model = Menu     # 关联menu模型
        fields = ['name', 'url', 'order', 'parent', 'icon', 'codename', 'is_visible']


class UserModelForm(forms.ModelForm):

    class Meta:
        model = User
        fields = ['username', 'mobile', 'is_staff', 'is_superuser', 'is_active', 'groups']


class GroupModelForm(forms.ModelForm):
    permissions = forms.ModelMultipleChoiceField(queryset=None, required=False, help_text='权限', label='权限')   # 多选框，label定义渲染在页面中的标题

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['permissions'].queryset = Permission.objects.filter(menu__is_deleted=False)
    class Meta:
        model = Group
        fields = ['name', 'permissions']


class NewsModelForm(forms.ModelForm):
    tag = forms.ModelChoiceField(queryset=None, required=False, help_text='分类', label='分类')
    content = forms.CharField(widget=CKEditorUploadingWidget(), label='内容')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['tag'].queryset = Tag.objects.filter(is_deleted=False)

    class Meta:
        model = News
        fields = ['title', 'is_deleted', 'digest', 'image_url', 'tag', 'content']
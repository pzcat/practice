# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author PZcat created at 2019/8/24 18:53

from haystack import indexes
from .models import News


class NewsIndex(indexes.SearchIndex, indexes.Indexable):
    """
    这个模型的作用类似于django的模型，它告诉haystack哪些数据会被放到查询返回的对象中，以及通过哪些字段进行索引和查询
    """
    text = indexes.CharField(document=True, use_template=True)   # 第一个字段是固定的，定义通过哪些字段进行索引和查询
    id = indexes.CharField(model_attr='id')
    title = indexes.CharField(model_attr='title')
    digest = indexes.CharField(model_attr='digest')
    content = indexes.CharField(model_attr='content')
    image_url = indexes.CharField(model_attr='image_url')

    def get_model(self):
        """
        返回建立索引的模型
        :return:
        """
        return News

    def index_queryset(self, using=None):
        """
        返回要建立索引的数据查询集
        :param using:
        :return:
        """
        return self.get_model().objects.filter(is_deleted=False)
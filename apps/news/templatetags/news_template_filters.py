# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author PZcat created at 2019/8/25 23:51
from django import template

register = template.Library()


@register.filter()
def page_bar(page):
    page_list = []
    '''    
    if page.number == 1:
        pass
    elif page.number == 2:
        page_list.append(1)
    elif page.number ==3:
        page.list.append(2)
    elif page.number > 4:
        page_list.append('...')
        page_list.append(page.number-2)
        page_list.append(page)
    '''
    # 当前页左边部分
    if page.number != 1:
        page_list.append(1)
    if page.number - 3 > 1:
        page_list.append('...')
    if page.number - 2 > 1:
        page_list.append(page.number - 2)    # 显示前两个页码
    if page.number - 1 > 1:
        page_list.append(page.number - 1)    # 显示前一个页码

    page_list.append(page.number)          # 当前页

    # 当前页右边部分
    if page.number + 1 < page.paginator.num_pages:
        page_list.append(page.number + 1)
    if page.number + 2 < page.paginator.num_pages:
        page_list.append(page.number + 2)
    if page.number + 3 < page.paginator.num_pages:
        page_list.append('...')
    if page.number != page.paginator.num_pages:
        page_list.append(page.paginator.num_pages)

    return page_list
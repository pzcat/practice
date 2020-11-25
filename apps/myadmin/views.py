import os
import logging

from django.conf import settings
from django.http import QueryDict, HttpResponse
from django.shortcuts import render, reverse
from django.views import View
from django.contrib.auth.models import Permission, Group
from django.contrib.contenttypes.models import ContentType
from django.core.paginator import Paginator
from django.contrib.auth.mixins import PermissionRequiredMixin

from .models import Menu
from .forms import MenuModelForm, UserModelForm, GroupModelForm, NewsModelForm
from utils.json_res import json_response
from utils.json_code import Code
from user.models import User
from news.models import News, Tag
from utils.ck_uploader.funcs import get_filename
from .generic import MyListView, MyUpdateView


logger = logging.getLogger('django')


class MyPermissionRequiredMixin(PermissionRequiredMixin):
    def has_permission(self):
        """
        覆盖父类方法，解决一个视图中不同请求，权限不同的问题
        :return:
        """
        perms = self.get_permission_required()
        if isinstance(perms, dict):
            if self.request.method.lower() in perms:
                return self.request.user.has_perms(perms[self.request.method.lower()])   # has_perms检查多个权限（对象是元组）
        else:
                return self.request.user.has_perms(perms)

    def handle_no_permission(self):
        """
        覆盖父类方法，解决ajax返回json数据的问题
        """
        # 没有权限有两种情况
        if self.request.is_ajax():            # 如果请求是ajax
            # 1.登录了，但用户没有权限
            if self.request.user.is_authenticated:
                return json_response(errno=Code.ROLEERR, errmsg='您没有权限！')
            # 2.没有登录
            else:
                return json_response(errno=Code.SESSIONERR, errmsg='您未登录，请登录！', data={'url': reverse(self.get_login_url())})
        else:
            return super().handle_no_permission()


class IndexView(View):
    # def get(self, request):
        # 写死的菜单
        # menus = [
        #     {
        #         "name": "工作台",
        #         "url": "myadmin:home",
        #         "icon": "fa-desktop"
        #     },
        #     {
        #         "name": "新闻管理",
        #         "icon": "fa-newspaper-o",
        #         "children": [
        #             {
        #                 "name": "新闻标签管理",
        #                 "url": "myadmin:wait"
        #             }, {
        #                 "name": "新闻管理",
        #                 "url": "myadmin:wait"
        #             }, {
        #                 "name": "热门新闻管理",
        #                 "url": "myadmin:wait"
        #             }
        #         ]
        #     },
        #     {
        #         "name": "轮播图管理",
        #         "icon": "fa-picture-o",
        #         "url": "myadmin:home"
        #     },
        #     {
        #         "name": "文档管理",
        #         "icon": "fa-folder",
        #         "url": "myadmin:home"
        #     },
        #     {
        #         "name": "在线课堂",
        #         "icon": "fa-book",
        #         "children": [
        #             {
        #                 "name": "课程分类管理",
        #                 "url": "myadmin:wait"
        #             },
        #             {
        #                 "name": "课程管理",
        #                 "url": "myadmin:wait"
        #             },
        #             {
        #                 "name": "讲师管理",
        #                 "url": "myadmin:wait"
        #             }
        #         ]
        #     },
        #     {
        #         "name": "系统设置",
        #         "icon": "fa-cogs",
        #         "children": [
        #             {
        #                 "name": "权限管理",
        #                 "url": "myadmin:wait"
        #             },
        #             {
        #                 "name": "用户管理",
        #                 "url": "myadmin:wait"
        #             },
        #             {
        #                 "name": "菜单管理",
        #                 "url": "myadmin:menu_list"
        #             },
        #             {
        #                 "name": "个人信息",
        #                 "url": "myadmin:wait"
        #             }
        #         ]
        #     }
        #
        # ]
        # 动态获取菜单
        # 拿到所有可用、可见菜单，并且是一级菜单
    def get(self, request):

        objs = Menu.objects.only('name', 'url', 'icon', 'permission__codename',
                                        'permission__content_type__app_label').select_related(
            'permission__content_type').filter(is_deleted=False, is_visible=True, parent=None)
        has_permissions = request.user.get_all_permissions()
        menus = []
        for menu in objs:
            if '%s.%s' % (menu.permission.content_type.app_label, menu.permission.codename) in has_permissions:
                temp = {
                    'name': menu.name,
                    'icon': menu.icon
                }

                children = menu.children.filter(is_deleted=False, is_visible=True)
                if children:
                    temp['children'] = []
                    for child in children:
                        if '%s.%s' % (
                        child.permission.content_type.app_label, child.permission.codename) in has_permissions:
                            temp['children'].append({
                                'name': child.name,
                                'url': child.url
                            })
                else:
                    if not menu.url:
                        continue
                    temp['url'] = menu.url
                menus.append(temp)
        print(menus)
        return render(request, 'myadmin/index.html', context={'menus': menus})


class HomeView(View):
    def get(self, request):
        return render(request, 'myadmin/home.html')


class WaitView(View):
    def get(self, request):
        return render(request, 'myadmin/wait.html')


class MenuListView(MyPermissionRequiredMixin, View):
    """
    菜单列表
    url: /admin/menus/
    """
    # permissions = 'myadmin.menu_list'
    permission_required = 'myadmin.menu_list'
    def get(self, request):
        # if not request.user.has_perm(self.permissions):
        #     return HttpResponse('对不起，您没有权限！')
        # 拿到一级菜单
        menus = Menu.objects.only('name', 'url', 'icon', 'is_visible', 'order', 'codename', 'is_deleted').filter(parent=None)

        return render(request, 'myadmin/menu/menu_list.html', context={'menus': menus})


class MenuAddView(View):
    """
    添加菜单视图
    url: /admin/menu/
    """
    def get(self, request):
        form = MenuModelForm()
        return render(request, 'myadmin/menu/add_menu.html', context={'form': form})

    def post(self, request):
        # 1.接收参数并验证
        form = MenuModelForm(request.POST)
        if form.is_valid():
            # 创建菜单
            new_menu = form.save()
            # 菜单的权限对象，菜单的外键
            content_type = ContentType.objects.filter(app_label='myadmin', model='menu').first()
            new_permission = Permission.objects.create(name=new_menu.name, content_type=content_type, codename=new_menu.codename)
            new_menu.permission = new_permission
            new_menu.save(update_fields=['permission'])    # 添加update参数可以提高性能
            return json_response(errmsg='添加菜单成功')
        else:
            return  render(request, 'myadmin/menu/add_menu.html', context={'form': form})


class MenuUpdateView(MyPermissionRequiredMixin, View):
    """
    url: /admin/menu/<int:menu_id>/
    """
    permission_required = {
        'get': ('myadmin.menu_update',),
        'put': ('myadmin.menu_update',),
        'delete': ('myadmin.menu_delete',)
    }

    def delete(self, request, menu_id):
        menu = Menu.objects.filter(id=menu_id).only('name')   # 没用first方法返回查询集

        if menu:
            menu = menu[0]
            # 验证是否为父菜单
            if menu.children.filter().exists():
                return json_response(errno=Code.DATAERR, errmsg='父菜单不能删除！')
            menu.permission.delete()            # 级联删除，删除了permission，menu也会被删除
            return json_response(errmsg='成功删除菜单%s!' % menu.name)
        else:
            return json_response(errno=Code.NODATA, errmsg='菜单不存在！')

    # 通过get请求渲染修改前表单数据
    def get(self, request, menu_id):
        menu = Menu.objects.filter(id=menu_id).first()
        form = MenuModelForm(instance=menu)             # 将对象字段传入表单
        return render(request, 'myadmin/menu/update_menu.html', context={'form': form})

    def put(self, request, menu_id):
        menu = Menu.objects.filter(id=menu_id).first()
        if not menu:
            return json_response(errno=Code.NODATA, errmsg="菜单不存在！")
        # 获取put请求参数
        put_data = QueryDict(request.body)     # put请求获取数据的方法和post不一样
        form = MenuModelForm(put_data, instance=menu)      # instance传入要修改的对象
        if form.is_valid():
            obj = form.save()
            # 检查修改了的字段是否和权限有关
            flag = False
            if 'name' in form.changed_data:               # form.changed_data:有变动的字段
                obj.permission.name = obj.name            # 修改对应permission中的name字段
                flag = True
            if 'codename' in form.changed_data:
                obj.permission.codename = obj.codename
                flag = True
            if flag:      # 如果有改动，才存储相应对象
                obj.permission.save()
            return json_response(errmsg="菜单修改成功！")
        else:
            return render(request, 'myadmin/menu/update_menu.html', context={'form': form})   # 如有异常渲染错误提示页面{% error %}


class UserListView(View):
    """
    用户列表视图
    url: /myadmin/users/
    """
    def get(self, request):
        # 1. 获取用户的查询集
        user_queryset = User.objects.only('username', 'is_active', 'mobile', 'is_staff', 'is_superuser')
        groups = Group.objects.only('name')
        # 2. 接收参数并校验

        # 3. 过滤
        # 过滤字典
        query_dict = {}
        groups__id = request.GET.get('group')
        if groups__id:
            try:
                groups__id = int(groups__id)
                query_dict['groups__id'] = groups__id
            except Exception as e:
                pass

        is_staff = request.GET.get('is_staff')
        if is_staff == '0':
            query_dict['is_staff'] = False
        if is_staff == '1':
            query_dict['is_staff'] = True

        is_superuser = request.GET.get('is_superuser')
        if is_superuser == '0':
            query_dict['is_superuser'] = False
        if is_superuser == '1':
            query_dict['is_superuser'] = True

        username = request.GET.get('username')
        if username:
            query_dict['username'] = username

        # 4. 分页
        try:
            page = int(request.GET.get('page', 1))
        except Exception as e:
            page = 1
        paginator = Paginator(user_queryset.filter(**query_dict), 2)

        current_page = paginator.get_page(page)
        # 5. 渲染模板
        context = {
            'users': current_page,
            'groups': groups
        }

        # 将查询条件返回前端
        context.update(query_dict)
        # 6. 返回
        return render(request, 'myadmin/user/user_list.html', context=context)


class UserUpdateView(View):
    """
    用户更新视图
    url: /myadmin/user/<int:user_id>/
    """
    def get(self, request, user_id):
        user = User.objects.filter(id=user_id).first()
        if user:
            form = UserModelForm(instance=user)    # 将拿到的user传入django的modelForm对象处理
        else:
            return json_response(errno=Code.NODATA, errmsg='找不到此用户！')
        return render(request, 'myadmin/user/user_detail.html', context={'form': form})

    def put(self, request, user_id):
        # 1. 拿到要修改的用户对象
        user = User.objects.filter(id=user_id).first()
        # 1.1 判断用户是否存在
        if not user:
            return json_response(errno=Code.NODATA, errmsg='找不到该用户')
        # 2. 拿到前端传递的参数
        put_data = QueryDict(request.body)
        # 3. 校验参数
        # 3.1 创建表单对象
        form = UserModelForm(put_data, instance=user)
        # 4. 如果成功，保存数据
        if form.is_valid():
            form.save()
            return json_response(errmsg='用户修改成功！')
        # 5. 如果不成功，返回渲染了错误提示信息的页面
        else:
            return render(request, 'myadmin/user/user_detail.html', context={'form': form})


class GroupListView(View):
    """
    分组列表视图
    url: /myadmin/groups/
    """
    def get(self, request):
        # 1. 拿到所有的分组
        groups = Group.objects.only('name').all()
        # 2. 渲染
        return render(request, 'myadmin/group/group_list.html', context={'groups': groups})


class GroupUpdateView(View):
    """
    分组更新视图
    url: /myadmin/group/<int:group_id>/
    """
    def get(self, request, group_id):
        # 1. 拿到要修改的分组
        group = Group.objects.filter(id=group_id).first()
        # 1.1 判断是否存在
        if not group:
            return json_response(errno=Code.NODATA, errmsg='没有此分组！')
        # 2. 创建表单
        form = GroupModelForm(instance=group)
        # 3. 拿到所有可用一级菜单
        menus = Menu.objects.only('name', 'permission_id').select_related(
            'permission').filter(is_deleted=False, is_visible=True, parent=None)
        # 4. 拿到当前组的可用权限
        permissions = group.permissions.only('id').all()
        # 5. 返回渲染html
        return render(request, 'myadmin/group/group_detail.html', context={'form': form,
                                                                           'menus': menus,
                                                                           'permissions': permissions})

    def put(self, request, group_id):
        # 1. 拿到要修改的分组
        group = Group.objects.filter(id=group_id).first()
        # 1.1 判断是否不存在
        if not group:
            return json_response(errno=Code.NODATA, errmsg='该分组不存在')
        # 2. 拿到前端传递的参数
        put_data = QueryDict(request.body)
        # 3. 校验参数
        # 3.1 创建表单对象
        form = GroupModelForm(put_data, instance=group)
        if form.is_valid():
            # 4. 如果成功，保存数据
            form.save()
            return json_response(errmsg='修改分组成功！')
        else:
            # 拿到所有可用一级菜单
            menus = Menu.objects.only('name', 'permission_id').select_related(
                'permission').filter(is_deleted=False, is_visible=True, parent=None)
            # 拿到当前组的可用权限
            permissions = group.permissions.only('id').all()
            # 渲染包含错误提示的页面
            return render(request, 'myadmin/group/group_detail.html', context={'form': form,
                                                                               'menus': menus,
                                                                               'permissions': permissions})


class GroupAddView(View):
    """
    添加分组视图
    url: /myadmin/group/
    """
    def get(self, request):
        # 1.创建一个空表单
        form = GroupModelForm()
        # 2.拿到所有可用一级菜单
        menus = Menu.objects.only('name', 'permission_id').select_related(
            'permission').filter(is_deleted=False, is_visible=True, parent=None)
        # 2.返回渲染表单
        return render(request, 'myadmin/group/group_detail.html', context={'form': form, 'menus': menus})

    def post(self, request):
        # 1.根据post的数据，创建表单对象
        form = GroupModelForm(request.POST)
        # 2.校验
        if form.is_valid():
            form.save()
            return json_response(errmsg='添加分组成功！')
        else:
            menus = Menu.objects.only('name', 'permission_id').select_related(
                'permission').filter(is_deleted=False, is_visible=True, parent=None)
            # 2.返回渲染表单
            return render(request, 'myadmin/group/group_detail.html', context={'form': form, 'menus': menus})


class NewsListView(MyPermissionRequiredMixin, View):
    """
    新闻列表视图
    url: /myadmin/news_list/
    """
    permission_required = ('myadmin.news_list',)

    def get(self, request):
        # 1.获取新闻查询集
        queryset = News.objects.only('title', 'tag__name', 'author__username', 'is_deleted').select_related('tag', 'author').all()
        tags = Tag.objects.only('name').filter(is_deleted=False)
        # 2.获取参数   # 3.过滤
        query_dict = {}
        tag_id = request.GET.get('tag')
        if tag_id:
            try:
                tag_id = int(tag_id)
                query_dict['tag_id'] = tag_id
                queryset = queryset.filter(tag_id=tag_id)
            except Exception as e:
                pass

        title = request.GET.get('title')
        if title:
            query_dict['title'] = title
            queryset = queryset.filter(title__contains=title)

        is_deleted = request.GET.get('is_deleted', '1')
        flag = False

        if is_deleted == '0':
            is_deleted = True
            flag = True

        if is_deleted == '1':
            is_deleted = False
            flag = True

        if flag:
            queryset = queryset.filter(is_deleted=is_deleted)

        query_dict['is_deleted'] = is_deleted
        # 4.分页
        paginator = Paginator(queryset, 10)
        try:
            page = int(request.GET.get('page', 1))
        except Exception as e:
            page = 1
        current_page = paginator.get_page(page)
        # 5.返回渲染页面
        context = {
            'news_list': current_page,
            'tags': tags
        }
        context.update(query_dict)
        return render(request, 'myadmin/news/news_list.html', context=context)


class NewsUpdateView(View):
    """
    新闻修改视图
    url: /myadmin/news/<int:news_id>/
    """
    def get(self, request, news_id):
        # 1. 拿到对应的新闻对象
        news = News.objects.filter(id=news_id).first()
        if news:
            # 2. 生成表单对象
            form = NewsModelForm(instance=news)
        else:
            return json_response(errno=Code.NODATA, errmsg='没有此新闻!')
        # 3. 渲染并返回
        return render(request, 'myadmin/news/news_detail.html', context={'form': form})

    def put(self, request, news_id):
        # 1. 拿到的要修改的对象
        news = News.objects.filter(id=news_id).first()
        if not news:
            return json_response(errno=Code.NODATA, errmsg='没有此新闻!')
        # 2. 获取put的数据
        put_data = QueryDict(request.body)
        # 3. 创建模型表单
        form = NewsModelForm(put_data, instance=news)
        # 4. 校验表单
        if form.is_valid():
            # 5. 如果成功，则保存数据并返回
            form.save()
            return json_response(errmsg='修改成功！')
        else:
            # 6. 如果失败，返回渲染错误信息的html
            return render(request, 'myadmin/news/news_detail.html', context={'form': form})


class UploadFileView(View):
    """
    上传文件视图
    url: /myadmin/upload/
    """
    def post(self, request):
        try:
            file = request.FILES['upload']
            filename = get_filename(file.name)

            file_path = os.path.join(settings.MEDIA_ROOT, filename)

            with open(file_path, 'wb') as f:
                for chunk in file.chunks():                 # file封装的文件对象
                    f.write(chunk)

            return json_response(data={
                'url': settings.MEDIA_URL + filename,
                'name': filename,
                'uploaded': '1'
            })
        except Exception as e:
            logger.error('上传文件失败：[%s]' % e)
            return json_response(data={'uploaded': '0'})


class NewsAddView(View):
    """
    添加新闻视图
    url: /myadmin/news/
    """
    def get(self, request):
        # 1. 创建一个模型表单对象（空）
        form = NewsModelForm()
        # 2. 返回渲染的html页面
        return render(request, 'myadmin/news/news_detail.html', context={'form': form})
    
    def post(self, request):
        # 1. 接收数据并创建模型表单对象
        form = NewsModelForm(request.POST)
        # 2. 校验
        if form.is_valid():
            # 3. 如果校验通过，保存数据
            instance = form.save(commit=False)           # commit=False 在本地保存，不连接数据库
            # 添加作者字段
            instance.author = request.user
            instance.save()                              # 连接数据库
            return json_response(errmsg='添加新闻成功！')
        else:
            # 4. 如果校验失败，就返回包含错误信息的html
            return render(request, 'myadmin/news/news_detail.html', context={'form': form})


class TagListView(MyPermissionRequiredMixin, MyListView):
    permission_required = ('myadmin.news_tag_list')
    model = Tag
    # template_name = 'myadmin/tag/tag_list.html'

    page_header = '系统设置'
    page_option = '新闻标签管理'
    table_title = '新闻标签列表'

    fields = ['name', 'is_deleted']


class TagUpdateView(MyPermissionRequiredMixin, MyUpdateView):
    permission_required = ('myadmin.news_tag_update')

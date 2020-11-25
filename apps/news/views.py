import logging

from django.shortcuts import render, get_object_or_404
from django.views import View
from django.db.models import F
from django.core.paginator import Paginator
from django.http import HttpResponseNotFound, HttpResponse
from haystack.generic_views import SearchView
from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin

from .models import Tag, News, HotNews, Banner, Comments
from . import constants
from utils.json_code import Code, error_map
from utils.json_res import json_response

app_name = 'news'


logger = logging.getLogger('django')


def index(request):
    """
    新闻首页视图
    url: /
    :param request:
    :return:
    """
    # 获取新闻标签
    tags = Tag.objects.only('name').filter(is_deleted=False)     # 只选取name字段

    # 新闻推荐，结果集切片选取前n条
    # hot_news = HotNews.objects.only('news__title', 'news__image_url', 'news__id').filter(is_deleted=False).order_by('priority', '-news__clicks')[:constants.SHOW_HOTNEWS_COUNT]
    hot_news = HotNews.objects.select_related('news').only('news__title', 'news__image_url', 'news__id').filter(is_deleted=False).order_by('priority', '-news__clicks')[:constants.SHOW_HOTNEWS_COUNT]
    '''
    当需要联合查询，如果有N级，不写.select_related，会n次创建数据库连接，效率低下--两种方式sql语句不同
    '''
    return render(request, 'news/index.html', context={
        'tags': tags,
        'hot_news': hot_news
    })


class NewsListView(View):
    """
    新闻列表视图
    url: /news/
    args: tag, page
    """
    def get(self, request):
        # 1. 获取参数
        try:
            tag_id = int(request.GET.get('tag', 0))  # 默认值为0
        except Exception as e:
            logger.error('标签错误： \n{}'.format(e))
            tag_id = 0

        try:
            page = int(request.GET.get('page', 1))  # 默认值为0
        except Exception as e:
            logger.error('页码错误： \n{}'.format(e))
            page = 1

        # 2. 获取查询集
        '''news_queryset = News.objects.values('id', 'title', 'digest', 'image_url', 'update_time', 'tag__name', 'author__username')
        这种写法不方便，因为最终需要返回的字段名为 author而不是tag__name
        '''
        news_queryset = News.objects.values('id', 'title', 'digest', 'image_url', 'update_time').annotate(tag_name=F('tag__name'), author=F('author__username'))
        # 过滤
        # if tag_id:
        #     news = news_queryset.filter(is_deleted=False, tag_id=tag_id)
        # else:
        #     news = news_queryset.filter(is_deleted=False)
        news = news_queryset.filter(is_deleted=False, tag_id=tag_id) or news_queryset.filter(is_deleted=False)

        # 3. 分页
        # 创建分页对象
        paginator = Paginator(news, constants.PER_PAGE_NEWS_COUNT)
        # 获取当前页数据
        current_page = paginator.get_page(page)
        # 4. 返回数据
        data = {
            'total_pages': paginator.num_pages,
            'news': list(current_page),
        }
        return json_response(data=data)


class NewsBannerView(View):
    """
    轮播图视图
    url: /news/banners/
    """
    def get(self, request):
        banners = Banner.objects.values('image_url', 'news_id').annotate(news_title=F('news__title')).filter(is_deleted=False)[:constants.SHOW_BANNER_COUNT]

        data = {
            'banners': list(banners)
        }

        return json_response(data=data)


class NewsDetailView(View):
    """
    新闻详情视图
    url: '/news/<int:news_id>/'
    """
    def get(self, request, news_id):
        # 1. 校验id是否存在
        # 2. 获取数据
        news = News.objects.select_related('tag', 'author').only('title', 'content', 'update_time', 'tag__name', 'author__username').filter(is_deleted=False, id=news_id).first()
        '''用get方法，如果找不到数据会报错，而用first方法找不到数据会返回none
        补充：方法二
        from django.shortcuts import render, get_object_or_404
        news_queryset = News.objects.select_related('tag', 'author').only('title', 'content', 'update_time', 'tag__name', 'author__username').first()
        
        news = get_object_or_404(news_queryset, is_deleted=False, id=news_id)   # 如果查询不到结果返回404页面
        return render(request, 'news/news_detail.html', context={'news': news})
        '''
        if news:
            # 获取评论
            comments = Comments.objects.select_related('author', 'parent').only('content', 'author__username', 'update_time', 'parent__author__username', 'parent__content', 'parent__update_time').filter(is_deleted=False, news_id=news_id)

            return render(request, 'news/news_detail.html', context={'news': news, 'comments': comments})
        else:
            return HttpResponseNotFound('<h1>Page not found</h1>')


class NewsCommentView(View):
    """
    添加评论视图
    url: /news/<int:news_id>/comment/
    """
    def post(self, request, news_id):
        # 是否登录
        if not request.user.is_authenticated:
            return json_response(errno=Code.SESSIONERR, errmsg=error_map[Code.SESSIONERR])

        # 新闻是否存在
        if not News.objects.filter(is_deleted=False, id=news_id).exists():
            return json_response(errno=Code.PARAMERR, errmsg='新闻新闻不存在')

        # 判断内容
        content = request.POST.get('content')
        if not content:
            return json_response(errno=Code.PARAMERR, errmsg='评论内容不能为空')

        # 父id 是否正常
        parent_id = request.POST.get('parent_id')
        if parent_id:
            try:
                parent_id = int(parent_id)
                if not Comments.objects.filter(is_deleted=False, id=parent_id, news_id=news_id).exists():
                    return json_response(errno=Code, errmsg=error_map[Code.PARAMERR])
            except Exception as e:
                logger.info('前端传递过来的parent_id异常\n{}'.format(e))
                return json_response(errn=Code.PARAMERR, errmsg='未知异常')

        # 保存到数据库
        new_comment = Comments()
        new_comment.content = content
        new_comment.news_id = news_id
        new_comment.author = request.user
        new_comment.parent_id = parent_id if parent_id else None

        new_comment.save()

        # 序列化可放到模型中

        return json_response(data=new_comment.to_dict_data())

class NewsSearchView(LoginRequiredMixin, SearchView):
    """
    新闻搜索视图
    url: '/news/search/'
    """
    template_name = 'news/search.html'

    def get(self, request, *args, **kwargs):
        # 1. 获取查询参数
        query = request.GET.get('q')
        if not query:
            # 2. 如果没有查询参数
            # 返回热门新闻
            hot_news = HotNews.objects.select_related('news__tag').only('news__title', 'news__image_url', 'news_id', 'news__tag__name').filter(is_deleted=False).order_by('priority', '-news__clicks')
            # 分页
            paginator = Paginator(hot_news, settings.HAYSTACK_SEARCH_RESULTS_PER_PAGE)
            try:
                page = paginator.get_page(int(request.GET.get('page')))
            except Exception as e:
                page = paginator.get_page(1)

            return render(request, self.template_name, context={
                'page': page,
                'query': query
            })
        else:
            # 3. 如果有查询参数
            return super().get(request, *args, **kwargs)

    def get_context_data(self, *args, **kwargs):
        """
        在context中添加变量page
        :param args:
        :param kwargs:
        :return:
        """
        context = super().get_context_data(*args, **kwargs)
        if context['page_obj']:
            context['page'] = context['page_obj']

        return context
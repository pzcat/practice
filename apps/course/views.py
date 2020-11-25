from django.shortcuts import render
from django.views import View
from django.http import Http404

from .models import Course


class IndexView(View):
    """
    在线课堂首页面
    url:/course/
    """
    def get(self, request):
        # 1.拿到所有的视频数据     only返回模型对象, values返回字典
        courses = Course.objects.only('title', 'cover_url', 'teacher__name', 'teacher__title').select_related(
            'teacher').filter(is_deleted=False)

        # 2.前端渲染
        return render(request, 'course/course.html', context={'courses': courses})


class CourseDetailView(View):
    """
    课程详情视图
    url: /course/<int:course_id>/
    """
    def get(self, request, course_id):
        # 1. 拿到课程信息
        course = Course.objects.only('title', 'cover_url', 'video_url', 'profile', 'outline', 'teacher__name', 'teacher__photo', 'teacher__title', 'teacher__profile').select_related('teacher').filter(is_deleted=False, id=course_id).first()
        # 2. 渲染
        if course:
            return render(request, 'course/course_detail.html', context={'course': course})
        else:
            return Http404('此课程不存在')
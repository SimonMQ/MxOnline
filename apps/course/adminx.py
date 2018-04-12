# coding:utf-8

import xadmin

from .models import Course, Lesson, Video, CourseResource


# 将course app中的models与后台管理器xadmin关联注册
# 并显示相应字段
# 此类继承自object。原admin为：class CourseAdmin(admin.ModelAdmin)
class CourseAdmin(object):
    list_display = ['name', 'desc', 'detail', 'degree', 'learn_times', 'students']
    search_fields = ['name', 'desc', 'detail', 'degree', 'students']
    list_filter = ['name', 'desc', 'detail', 'degree', 'learn_times', 'students']


class LessonAdmin(object):
    list_display = ['course', 'name', 'add_time']
    search_fields = ['course', 'name']
    # 由于course是一个外键，所以过滤的时候根据课程名称过滤，即course.name
    list_filter = ['course__name', 'name', 'add_time']


class VideoAdmin(object):
    list_display = ['lesson', 'name', 'add_time']
    search_fields = ['lesson', 'name']
    list_filter = ['lesson', 'name', 'add_time']


class CourseResourceAdmin(object):
    list_display = ['course', 'name', 'download', 'add_time']
    search_fields = ['course', 'name', 'download']
    # 由于course是一个外键，所以过滤的时候根据课程名称过滤，即course.name
    list_filter = ['course__name', 'name', 'download', 'add_time']


# models与xadmin关联注册
xadmin.site.register(Course, CourseAdmin)
xadmin.site.register(Lesson, LessonAdmin)
xadmin.site.register(Video, VideoAdmin)
xadmin.site.register(CourseResource, CourseResourceAdmin)

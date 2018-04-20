# coding:utf-8
from django.urls import path, re_path
from .views import CourseView


app_name = 'course'

urlpatterns = [
    path('list/', CourseView.as_view(), name='course_list'),
]

from django.shortcuts import render
from django.views.generic import View


class CourseView(View):
    def get(self, request):
        context = ''
        return render(request, 'course-list.html', context=context)

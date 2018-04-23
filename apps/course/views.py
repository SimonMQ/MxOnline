from django.shortcuts import render
from django.http import HttpResponse
from django.views.generic import View
from .models import Course, CourseResource, Video
from pure_pagination import Paginator, PageNotAnInteger
from operation.models import UserFavorite, CourseComments, UserCourse
from utils.mixin_utils import LoginRequiredMixin
from django.db.models import Q


class CourseView(View):
    def get(self, request):
        current_list = 'courses'
        all_courses = Course.objects.all()
        hot_courses = all_courses.order_by('-click_nums')[:5]

        # 搜索功能
        # 使用并集查询功能，过滤出符合条件的搜索内容
        search_keywords = request.GET.get('keywords', '')
        if search_keywords:
            all_courses = all_courses.filter(Q(name__icontains=search_keywords) |
                                             Q(desc__icontains=search_keywords) |
                                             Q(detail__icontains=search_keywords))

        # 排序
        sort = request.GET.get('sort', '')
        if not sort:
            all_courses = all_courses.order_by('-add_time')
        elif sort == 'students':
            all_courses = all_courses.order_by('-students')
        elif sort == 'hot':
            all_courses = all_courses.order_by('-click_nums')

        # 分页
        try:
            page = request.GET.get('page', 1)
        except PageNotAnInteger:
            page = 1
        p = Paginator(all_courses, 9, request=request)
        courses = p.page(page)

        context = {
            'all_courses': courses,
            'hot_courses': hot_courses,
            'sort': sort,
            'current_list': current_list,
        }
        return render(request, 'course-list.html', context=context)


class CourseDetailView(View):
    def get(self, request, course_id):
        course = Course.objects.get(id=int(course_id))
        # 课程点击数+1
        course.click_nums += 1
        course.save()

        has_fav_course = False
        has_fav_org = False
        if request.user.is_authenticated:
            if UserFavorite.objects.filter(user=request.user, fav_id=course.id, fav_type=1):
                has_fav_course = True
            if UserFavorite.objects.filter(user=request.user, fav_id=course.course_org.id, fav_type=2):
                has_fav_org = True

        # 根据标签推荐课程
        tag = course.tag
        if tag:
            relate_courses = Course.objects.filter(tag=tag)[:5]
        else:
            relate_courses = []

        # 该课程所属机构
        course_org = course.course_org
        all_orgcourses = course_org.course_set.all()
        course_onums = all_orgcourses.count()
        all_orgteachers = course_org.teacher_set.all()
        teacher_onums = all_orgteachers.count()

        context = {
            'course': course,
            'course_org': course_org,
            'course_onums': course_onums,
            'teacher_onums': teacher_onums,
            'has_fav_course': has_fav_course,
            'has_fac_org': has_fav_org,
            'relate_courses': relate_courses,
        }
        return render(request, 'course-detail.html', context=context)


class CourseInfoView(LoginRequiredMixin, View):
    def get(self, request, course_id):
        # 根据课程id获取课程对象
        course = Course.objects.get(id=int(course_id))

        # 筛选一个符合该(用户/课程)的用户课程对象,如果不存在,那么创建一个对象,并保存
        user_courses = UserCourse.objects.filter(user=request.user, course=course)
        if not user_courses:
            user_course = UserCourse(user=request.user, course=course)
            user_course.save()

        user_courses = UserCourse.objects.filter(course=course)
        user_ids = [user_course.user_id for user_course in user_courses]
        all_user_courses = UserCourse.objects.filter(user_id__in=user_ids)
        course_ids = [all_user_course.course_id for all_user_course in all_user_courses]
        relate_courses = Course.objects.filter(id__in=course_ids).order_by('-click_nums')[:5]

        # 课程资源
        all_resources = CourseResource.objects.filter(course=course)
        context = {
            'course': course,
            'relate_courses': relate_courses,
            'all_resources': all_resources,
        }
        return render(request, 'course-video.html', context=context)


class CourseCommentView(LoginRequiredMixin, View):
    def get(self, request, course_id):
        course = Course.objects.get(id=int(course_id))
        course_comments = CourseComments.objects.filter(course=course)

        user_courses = UserCourse.objects.filter(course=course)
        user_ids = [user_course.user_id for user_course in user_courses]
        all_user_courses = UserCourse.objects.filter(user_id__in=user_ids)
        course_ids = [all_user_course.course_id for all_user_course in all_user_courses]
        relate_courses = Course.objects.filter(id__in=course_ids).order_by('-click_nums')[:5]
        context = {
            'course': course,
            'course_comments': course_comments,
            'relate_courses': relate_courses,
        }
        return render(request, 'course-comment.html', context=context)


class AddCommentView(View):
    def post(self, request):
        if not request.user.is_authenticated:
            return HttpResponse('{"status": "fail", "msg": "用户未登录"}', content_type='application/json')
        course_id = request.POST.get('course_id', 0)
        comments = request.POST.get('comments', '')
        if int(course_id) > 0 and comments:
            # 实例化一个CourseComments对象，用以保存评论数据至db
            course_comments = CourseComments()
            course = Course.objects.get(id=int(course_id))
            course_comments.course = course
            course_comments.comments = comments
            course_comments.user = request.user
            course_comments.save()

            return HttpResponse('{"status": "success", "msg": "评论成功"}', content_type='application/json')
        else:
            return HttpResponse('{"status": "fail", "msg": "评论失败"}', content_type='application/json')


class VideoPlayView(LoginRequiredMixin, View):
    def get(self, request, video_id):
        video = Video.objects.get(id=int(video_id))
        # video-->lesson-->course
        course = video.lesson.course

        course.students += 1
        course.save()

        user_courses = UserCourse.objects.filter(user=request.user, course=course)
        if not user_courses:
            user_course = UserCourse(user=request.user, course=course)
            user_course.save()

        user_courses = UserCourse.objects.filter(course=course)
        user_ids = [user_course.user_id for user_course in user_courses]
        all_user_courses = UserCourse.objects.filter(user_id__in=user_ids)
        course_ids = [all_user_course.course_id for all_user_course in all_user_courses]
        relate_courses = Course.objects.filter(id__in=course_ids).order_by('-click_nums')[:5]

        # 课程资源
        all_resources = CourseResource.objects.filter(course=course)

        context = {
            'course': course,
            'all_resources': all_resources,
            'relate_courses': relate_courses,
            'video': video,

        }
        return render(request, 'course-play.html', context=context)

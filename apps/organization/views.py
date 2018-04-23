from django.shortcuts import render
from django.views.generic.base import View
from django.db.models import Q
from .models import CourseOrg, CityDict, Teacher
from course.models import Course
from pure_pagination import PageNotAnInteger, Paginator
from django.http import HttpResponse
from .forms import UserAskForm
from operation.models import UserFavorite


# 课程机构页面
class OrgView(View):
    def get(self, request):
        current_list = 'orgs'
        # 获取所有课程机构、机构数目、城市
        all_orgs = CourseOrg.objects.all()
        all_citys = CityDict.objects.all()

        # 搜索功能
        # 使用并集查询功能，过滤出符合条件的搜索内容
        search_keywords = request.GET.get('keywords', '')
        if search_keywords:
            all_orgs = all_orgs.filter(Q(name__icontains=search_keywords) |
                                       Q(desc__icontains=search_keywords))

        hot_orgs = all_orgs.order_by('-click_nums')[:5]

        # 类别筛选
        category = request.GET.get('ct', '')
        if category:
            all_orgs = all_orgs.filter(category=category)

        # 尝试从url中获取key为city的value，即city的id。如果不存在，返回空字符串。
        #  根据获取的city的id，过滤出机构列表
        city_id = request.GET.get('city', '')
        if city_id:
            all_orgs = all_orgs.filter(city_id=int(city_id))

        # 筛选后的机构数目
        org_onums = all_orgs.count()

        # 排序
        sort = request.GET.get('sort', '')
        if sort:
            if sort == 'students':
                all_orgs = all_orgs.order_by('-students')
            elif sort == 'courses':
                all_orgs = all_orgs.order_by('-course_nums')

        # 对课程机构进行分页
        # 尝试获取url中是否指定了页码，如果没有则返回第一页
        try:
            page = request.GET.get('page', 1)
        except PageNotAnInteger:
            page = 1
        # 分页，每页显示5个机构内容
        p = Paginator(all_orgs, 4, request=request)
        # 返回某页的分页对象
        orgs = p.page(page)

        context = {
            'all_orgs': orgs,
            'all_citys': all_citys,
            'org_onums': org_onums,
            'hot_orgs': hot_orgs,
            'category': category,
            'city_id': city_id,
            'current_list': current_list,
            'sort': sort,
        }
        return render(request, 'org-list.html', context=context)


# 用户添加咨询
class AddUserAskView(View):
    def post(self, request):
        userask_form = UserAskForm(request.POST)
        if userask_form.is_valid():
            user_ask = userask_form.save(commit=True)
            # 返回给前端一个json数据，HttpResponse可以指定传递的数据类型
            return HttpResponse('{"status": "success"}', content_type='application/json')
        else:
            return HttpResponse('{"status": "fail", "msg": "添加出错"}', content_type='application/json')


class OrgHomeView(View):
    def get(self, request, org_id):
        # 根据id获取该机构，然后获取该机构的所有课程和所有教师
        # 由于机构与它所属的课程/教师之间是外键链接的，所以用_set方法获取它们的所有数据
        current_page = 'home'
        course_org = CourseOrg.objects.get(id=int(org_id))
        all_courses = course_org.course_set.all()[:4]
        all_teachers = course_org.teacher_set.all()[:4]
        has_fav = False
        if request.user.is_authenticated:
            if UserFavorite.objects.filter(user=request.user, fav_id=course_org.id, fav_type=2):
                has_fav = True
        context = {
            'course_org': course_org,
            'all_courses': all_courses,
            'all_teachers': all_teachers,
            'current_page': current_page,
            'has_fav': has_fav,
        }
        return render(request, 'org-detail-homepage.html', context=context)


class OrgCourseView(View):
    def get(self, request, org_id):
        current_page = 'course'
        course_org = CourseOrg.objects.get(id=int(org_id))
        all_courses = course_org.course_set.all()[:4]
        has_fav = False
        if request.user.is_authenticated:
            if UserFavorite.objects.filter(user=request.user, fav_id=course_org.id, fav_type=2):
                has_fav = True
        context = {
            'course_org': course_org,
            'all_courses': all_courses,
            'current_page': current_page,
            'has_fav': has_fav,
        }
        return render(request, 'org-detail-course.html', context=context)


class OrgTeacherView(View):
    def get(self, request, org_id):
        current_page = 'teacher'
        course_org = CourseOrg.objects.get(id=int(org_id))
        all_teachers = course_org.teacher_set.all()[:4]
        has_fav = False
        if request.user.is_authenticated:
            if UserFavorite.objects.filter(user=request.user, fav_id=course_org.id, fav_type=2):
                has_fav = True
        context = {
            'course_org': course_org,
            'all_teachers': all_teachers,
            'current_page': current_page,
            'has_fav': has_fav,
        }
        return render(request, 'org-detail-teachers.html', context=context)


class OrgDescView(View):
    def get(self, request, org_id):
        current_page = 'desc'
        course_org = CourseOrg.objects.get(id=int(org_id))
        has_fav = False
        if request.user.is_authenticated:
            if UserFavorite.objects.filter(user=request.user, fav_id=course_org.id, fav_type=2):
                has_fav = True
        context = {
            'course_org': course_org,
            'current_page': current_page,
            'has_fav': has_fav,
        }
        return render(request, 'org-detail-desc.html', context=context)


class AddFavView(View):
    def post(self, request):
        fav_id = request.POST.get('fav_id', 0)
        fav_type = request.POST.get('fav_type', 0)

        if not request.user.is_authenticated:
            return HttpResponse('{"status": "fail", "msg": "用户未登录"}', content_type='application/json')
        exist_record = UserFavorite.objects.filter(user=request.user, fav_id=int(fav_id), fav_type=int(fav_type))
        if exist_record:
            exist_record.delete()
            return HttpResponse('{"status": "fail", "msg": "已取消收藏"}', content_type='application/json')
        else:
            user_fav = UserFavorite()
            if int(fav_id) > 0 and int(fav_type) > 0:
                user_fav.user = request.user
                user_fav.fav_id = int(fav_id)
                user_fav.fav_type = int(fav_type)
                user_fav.save()
                return HttpResponse('{"status": "success", "msg": "已收藏"}', content_type='application/json')
            else:
                return HttpResponse('{"status": "fail", "msg": "收藏出错"}', content_type='application/json')


class TeacherListView(View):
    def get(self, request):
        current_list = 'teachers'
        all_teachers = Teacher.objects.all()

        # 搜索功能
        # 使用并集查询功能，过滤出符合条件的搜索内容,i表示不区分大小写
        search_keywords = request.GET.get('keywords', '')
        if search_keywords:
            all_teachers = all_teachers.filter(name__icontains=search_keywords)

        hot_teachers = Teacher.objects.order_by('-click_nums')
        teacher_nums = all_teachers.count()

        sort = request.GET.get('sort', '')
        if sort == 'hot':
            all_teachers = all_teachers.order_by('-click_nums')

        try:
            page = request.GET.get('page', 1)
        except PageNotAnInteger:
            page = 1
        # 分页，每页显示5个机构内容
        p = Paginator(all_teachers, 4, request=request)
        # 返回某页的分页对象
        teachers = p.page(page)

        context = {
            'current_list': current_list,
            'all_teachers': teachers,
            'hot_teachers': hot_teachers,
            'teacher_nums': teacher_nums,
            'sort': sort,
        }
        return render(request, 'teacher-list.html', context=context)


class TeacherDetailView(View):
    def get(self, request, teacher_id):
        teacher = Teacher.objects.get(id=int(teacher_id))
        org = teacher.org
        org_teachers = Teacher.objects.filter(org=org).order_by('-click_nums')

        # 教师收藏和机构收藏
        has_teacher_faved = False
        if UserFavorite.objects.filter(user=request.user, fav_type=3, fav_id=teacher.id):
            has_teacher_faved = True

        has_org_faved = False
        if UserFavorite.objects.filter(user=request.user, fav_type=2, fav_id=teacher.org.id):
            has_org_faved = True

        teacher_courses = Course.objects.filter(teacher=teacher)
        try:
            page = request.GET.get('page', 1)
        except PageNotAnInteger:
            page = 1
        # 分页，每页显示5个机构内容
        p = Paginator(teacher_courses, 4, request=request)
        # 返回某页的分页对象
        t_courses = p.page(page)

        context = {
            'teacher': teacher,
            'org': org,
            'org_teachers': org_teachers,
            'teacher_courses': t_courses,
            'has_teacher_faved': has_teacher_faved,
            'has_org_faved': has_org_faved,
        }
        return render(request, 'teacher-detail.html', context=context)

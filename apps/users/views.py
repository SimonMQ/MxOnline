from django.shortcuts import render
from django.contrib.auth import authenticate, login
from django.contrib.auth.backends import ModelBackend
from .models import UserProfile, EmailVerifyRecord
from django.db.models import Q
from django.views.generic.base import View
from .forms import LoginForm, RegisterForm
from django.contrib.auth.hashers import make_password
from utils.email_send import send_register_email


# 登陆视图，继承自ModelBackend，其中有个authenticate方法
# 邮箱和用户名都可以登陆
class CustomBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            # 从用户模型中获取用户名，Q为使用并集查询（用户名和邮箱二选一）
            user = UserProfile.objects.get(Q(username=username) | Q(email=username))
            # 判断密码是否正确，由于django后台密码加密，所以只能调用下面的方法来判断
            if user.check_password(password):
                return user
        except Exception as e:
            return None


# 登陆视图，如果请求为POST，且账号密码正确，则登陆，否则返回一个错误信息
# 如果请求为GET，再次载入登陆页面
class LoginView(View):
    def get(self, request):
        return render(request, 'login.html')

    def post(self, request):
        login_form = LoginForm(request.POST)
        if login_form.is_valid():
            # 获取用户名和密码
            user_name = request.POST.get('username', None)
            pass_word = request.POST.get('password', None)
            # authenticate方法--参数验证成功，则返回user对象，失败则返回None
            user = authenticate(username=user_name, password=pass_word)
            # user非None则说明验证成功
            if user is not None:
                # 只有注册激活才能登陆
                if user.is_acitve:
                    login(request, user)
                    return render(request, 'index.html')
                else:
                    return render(request, 'login.html', {'msg': '用户名或密码错误', 'login_form': login_form})
            else:
                return render(request, 'login.html', {'msg': '用户名或密码错误', 'login_form': login_form})
        # 如果form不合法，则不用返回错误信息msg。直接重新渲染
        else:
            return render(request, 'login.html', {'login_form': login_form})


class RegisterView(View):
    def get(self, request):
        register_form = RegisterForm()
        context = {
            'register_form': register_form,
        }
        return render(request, 'register.html', context=context)

    def post(self, request):
        register_form = RegisterForm(request.POST)
        if register_form.is_valid():
            user_name = request.POST.get('email', None)
            # 如果在用户信息数据库中找到同名字段，说明用户已存在
            if UserProfile.objects.filter(email=user_name):
                return render(request, 'register.html', {'register_form': register_form, 'msg': '用户已存在'})

            pass_word = request.POST.get('password', None)
            # 创建一个实例对象，保存相关信息到数据库
            user_profile = UserProfile()
            user_profile.username = user_name
            user_profile.email = user_name
            # 邮箱激活状态：只要用户去邮箱激活后才为True
            user_profile.is_active = False
            # 保存密码，并加密
            user_profile.password = make_password(pass_word)
            user_profile.save()
            send_register_email(user_name, 'register')
            return render(request, 'login.html')
        else:
            return render(request, 'register.html', {'register_from': register_form})


class ActiveUserView(View):
    def get(self, request, active_code):
        all_record = EmailVerifyRecord.objects.filter(code=active_code)
        if all_record:
            for record in all_record:
                email = record.mail
                user = UserProfile.objects.get(email=email)
                user.is_active = True
                user.save()
        else:
            return render(request, 'active_fail.html')
        return render(request, 'login.html')

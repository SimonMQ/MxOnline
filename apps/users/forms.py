# coding:utf-8

from django import forms
from captcha.fields import CaptchaField


class LoginForm(forms.Form):
    # 用户名密码不能为空，且密码不小于5个字符
    username = forms.CharField(required=True)
    password = forms.CharField(required=True, min_length=5)


# 注册验证表单，验证码字段内可定义错误提示信息
class RegisterForm(forms.Form):
    email = forms.EmailField(required=True)
    password = forms.CharField(required=True, min_length=5)
    captcha = CaptchaField()

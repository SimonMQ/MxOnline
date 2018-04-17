# coding:utf-8

import random
from django.core.mail import send_mail

from users.models import EmailVerifyRecord
from MxOnline.settings import EMAIL_FROM


# 生成随机字符串
def random_str(random_length=8):
    rd_str = ''
    chars = 'AaBbCcDdEeFfGgHhIiJjKkLlMmNnOoPpQqRrSsTtUuVvWwXxYyZz0123456789'
    for i in range(random_length):
        rd_str += chars[random.randint(0, (len(chars) - 1))]
    return rd_str


# 发送邮件方法，包含：注册激活码、忘记密码、修改邮箱三个功能
def send_register_email(email, send_type="register"):
    # 实例一个邮箱验证码对象，生成随机的16位code，获取其邮箱地址，发送方式，并保存至数据库
    email_record = EmailVerifyRecord()
    code = random_str(16)
    email_record.code = code
    email_record.email = email
    email_record.send_type = send_type
    email_record.save()

    # 定义邮件内容：主题、正文
    email_title = ""
    email_body = ""

    if send_type == "register":
        email_title = "Simon注册激活链接"
        email_body = "请点击下面的链接激活你的账号： http://127.0.0.1:8000/active/{0}".format(code)
        # 使用django内置的send_mail函数发送邮件
        # 四个参数：主题、正文、发件人邮箱地址、收件人邮箱地址(list，可以同时发送多个)
        send_status = send_mail(email_title, email_body, EMAIL_FROM, [email])
        # 如果发送成功
        if send_status:
            pass
    elif send_type == 'forget':
        email_title = "Simon忘记密码重置链接"
        email_body = "请点击下面的链接重置你的密码： http://127.0.0.1:8000/reset/{}".format(code)
        send_status = send_mail(email_title, email_body, EMAIL_FROM, [email])
        if send_status:
            pass
    elif send_type == 'update_email':
        pass

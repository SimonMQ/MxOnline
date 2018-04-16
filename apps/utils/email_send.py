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


# 发送邮件
def send_register_email(email, send_type="register"):
    # 实例一个验证码对象
    email_record = EmailVerifyRecord()
    # 生成随机的16位code
    code = random_str(16)
    # 将数据保存至实例中
    email_record.code = code
    email_record.email = email
    email_record.send_type = send_type
    # 保存至数据库
    email_record.save()
    # 定义邮件内容
    email_title = ""
    email_body = ""

    if send_type == "register":
        email_title = "Simon注册激活链接"
        email_body = "请点击下面的链接激活你的账号： http://127.0.0.1:8000/active/{0}".format(code)
        send_status = send_mail(email_title, email_body, EMAIL_FROM, [email])
        if send_status:
            pass

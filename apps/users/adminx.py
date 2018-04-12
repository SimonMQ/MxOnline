# coding:utf-8

import xadmin

from xadmin import views
from .models import EmailVerifyRecord, Banner


# 将users app中的models注册到xadmin中
# 并显示相应字段
# 此类继承自object，而不再是admin
class EmailVerifyRecordAdmin(object):
    list_display = ['code', 'email', 'send_type', 'send_time']
    search_fields = ['code', 'email', 'send_type']
    list_filter = ['code', 'email', 'send_type', 'send_time']


class BannerAdmin(object):
    list_display = ['title', 'image', 'url', 'index', 'add_time']
    search_fields = ['title', 'image', 'url', 'index']
    list_filter = ['title', 'image', 'url', 'index', 'add_time']


xadmin.site.register(EmailVerifyRecord, EmailVerifyRecordAdmin)
xadmin.site.register(Banner, BannerAdmin)


# 创建xadmin的基本管理器配置，并与view绑定
class BaseSetting(object):
    # 开启主题功能(在xadmin右上角显示“主题”菜单)
    enable_themes = True
    use_bootswatch = True


xadmin.site.register(views.BaseAdminView, BaseSetting)


# 全局修改
class GlobalSettings(object):
    # 修改左上角title
    site_title = 'Simon后台管理器'
    # 修改底部footer
    site_footer = 'Simon的公司'
    # 将左侧菜单栏折叠
    menu_style = 'accordion'


# 注册
xadmin.site.register(views.CommAdminView, GlobalSettings)

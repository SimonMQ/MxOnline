from django.apps import AppConfig


class CourseConfig(AppConfig):
    name = 'course'
    # 修改后台管理界面xadmin的左侧菜单栏，显示名称为中文
    # 其默认排序方式为：nav_menu.sort(key=lambda x: x['title'])
    # 但是如果要将其按中文排序，方法是什么呢？
    verbose_name = '课程'

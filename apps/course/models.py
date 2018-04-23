from datetime import datetime

from django.db import models
from organization.models import CourseOrg, Teacher


# Create your models here.
# 课程TABLE
class Course(models.Model):
    DEGREE_CHOICES = (
        ('cj', '初级'),
        ('zj', '中级'),
        ('gj', '高级')
    )

    name = models.CharField('课程名', max_length=50)
    desc = models.CharField('课程描述', max_length=300)
    detail = models.TextField('课程详情')
    degree = models.CharField('难度', choices=DEGREE_CHOICES, max_length=2)
    learn_times = models.IntegerField('学习时常(分钟数)', default=0)
    students = models.IntegerField('学习人数', default=0)
    fav_nums = models.IntegerField('收藏人数', default=0)
    image = models.ImageField('封面图', upload_to='courses/%Y%m', max_length=100)
    click_nums = models.IntegerField('点击数', default=0)
    add_time = models.DateTimeField('添加时间', default=datetime.now)
    course_org = models.ForeignKey(CourseOrg, verbose_name='所属机构', on_delete=models.CASCADE, null=True, blank=True)
    category = models.CharField('课程类别', max_length=20, default='')
    tag = models.CharField('课程标签', max_length=20, default='')
    teacher = models.ForeignKey(Teacher, verbose_name='课程讲师', on_delete=models.CASCADE, null=True, blank=True)
    youneed_know = models.CharField('课程须知', max_length=300, default='')
    teacher_tell = models.CharField('老师告诉你', max_length=300, default='')

    class Meta:
        verbose_name = '课程'
        verbose_name_plural = verbose_name

    # 获取课程的章节
    def get_course_lessons(self):
        return self.lesson_set.all()

    # 获取课程的章节数
    def get_zj_nums(self):
        return self.lesson_set.all().count()

    # 获取所有学习该课程的用户
    def get_learn_users(self):
        return self.usercourse_set.all()[:5]

    def __str__(self):
        return self.name


# 章节信息TABLE，每个章节属于课程的一部分，用外键指向Course
class Lesson(models.Model):
    course = models.ForeignKey(Course, verbose_name='课程', on_delete=models.CASCADE)
    name = models.CharField('章节名', max_length=100)
    add_time = models.DateTimeField('添加时间', default=datetime.now)

    class Meta:
        verbose_name = '章节'
        verbose_name_plural = verbose_name

    # 获取章节的所有视频
    def get_lesson_videos(self):
        return self.video_set.all().order_by('name')

    def __str__(self):
        return '《{}》课程的章节 >> {}'.format(self.course, self.name)


# videoTABLE，用外键指向Lesson
class Video(models.Model):
    lesson = models.ForeignKey(Lesson, verbose_name='章节', on_delete=models.CASCADE)
    name = models.CharField('视频名', max_length=100)
    learn_times = models.IntegerField('学习时长(分钟数)', default=0)
    url = models.CharField('访问地址', max_length=200, default='')
    add_time = models.DateTimeField('添加时间', default=datetime.now)

    class Meta:
        verbose_name = '视频'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


# 课程资源TABLE，用外键指向Course
class CourseResource(models.Model):
    course = models.ForeignKey(Course, verbose_name='课程', on_delete=models.CASCADE)
    name = models.CharField('资源名', max_length=100)
    download = models.FileField('资源文件', upload_to='course/resource/%Y/%m', max_length=100)
    add_time = models.DateTimeField('添加时间', default=datetime.now)

    class Meta:
        verbose_name = '课程资源'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name

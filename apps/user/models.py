from django.db import models

from django.contrib.auth.models import AbstractUser, UserManager as _UserManager

# Create your models here.


class UserManager(_UserManager):
    """
    自定义管理器，用来修改使用createsuperuser命令创建用户必须输入email的行为
    """
    def create_superuser(self, username, password, email=None, **extra_fields):
        super().create_superuser(username=username, password=password, email=email, **extra_fields)

class User(AbstractUser):
    """
    自定义的User模型，添加mobile, email_active字段
    """

    mobile = models.CharField('手机号', max_length=11, unique=True, help_text='手机号', error_messages={'unique': '此手机号已注册'})

    email_active = models.BooleanField('邮箱状态', default=False)

    class Meta:
        db_table = 'tb_user'       # 指定数据库表名
        verbose_name = '用户'       # 在admin站点中的显示名称
        verbose_name_plural = verbose_name        # 复数？

    def __str__(self):
        return self.username

    # 当通过 createsuperuser 命令创建一个user对象时需要的字段
    REQUIRED_FIELDS = ['mobile']

    # 修改必须输入email的行为，通过管理器 objects(此处为UserManager)
    objects = UserManager()
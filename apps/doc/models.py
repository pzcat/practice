from django.db import models

from utils.models import BaseModel


class Doc(BaseModel):
    """
    文件模型
    """
    file_url = models.URLField('文件url', help_text='文件url')
    file_name = models.CharField('文件名', max_length=48, help_text='文件名')
    title = models.CharField('文件标题', max_length=150, help_text='文件标题')
    desc = models.TextField('文件描述', help_text='文件描述')
    image_url = models.URLField('封面图片url', help_text='封面图片url')
    author = models.ForeignKey('user.User', on_delete=models.SET_NULL, null=True)

    class Meta:
        db_table = 'tb_docs'               # 数据库表名
        verbose_name = '文件表'            # 后台管理站点显示的名称
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.title

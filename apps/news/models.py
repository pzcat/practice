from django.db import models
from ckeditor_uploader.fields import RichTextUploadingField

from utils.models import BaseModel
from utils.validators import MediaUrlValidator



class Tag(BaseModel):
    """
    文章分类标签模型
    """
    name = models.CharField(verbose_name='标签名', max_length=64, help_text='标签名')

    class Meta:
        ordering = ['-update_time', '-id']                      # 排序
        db_table = "tb_tag"                                     # 数据库中表名
        verbose_name = "文章标签"                               # 在admin站点中显示的名称
        verbose_name_plural = verbose_name                      # 显示的复数名称

    def __str__(self):
        return self.name


class News(BaseModel):
    """
    文章模型
    """
    title = models.CharField('标题', max_length=150, help_text='标题')
    digest = models.CharField('摘要', max_length=200, help_text='摘要')
    content = RichTextUploadingField('内容', help_text='内容')
    clicks = models.IntegerField('点击量', default=0, help_text='点击量')
    image_url = models.CharField('图片url', default='', help_text='图片url', max_length=200, validators=[MediaUrlValidator()])

    tag = models.ForeignKey('Tag', on_delete=models.SET_NULL, null=True)     # 删除文章分类不删除文章，该字段可为空
    author = models.ForeignKey('user.User', on_delete=models.SET_NULL, null=True)     # 文章作者，也是一对多

    class Meta:
        ordering = ['-update_time', '-id']                      # 排序
        db_table = "tb_news"                                     # 数据库中表名
        verbose_name = "新闻"                               # 在admin站点中显示的名称
        verbose_name_plural = verbose_name                      # 显示的复数名称

    def __str__(self):
        return self.title


class Comments(BaseModel):
    """
    评论模型
    """
    content = models.TextField('内容', help_text='内容')
    author = models.ForeignKey('user.User', on_delete=models.SET_NULL, null=True)
    news = models.ForeignKey('News', on_delete=models.CASCADE)

    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True)

    class Meta:
        ordering = ['-update_time', '-id']                      # 排序
        db_table = "tb_comments"                                     # 数据库中表名
        verbose_name = "评论"                               # 在admin站点中显示的名称
        verbose_name_plural = verbose_name                      # 显示的复数名称

    def __str__(self):
        return '<评论{}>'.format(self.id)

    def to_dict_data(self):
        comment_dict = {
            'news_id': self.news_id,
            'content_id': self.id,
            'content': self.content,
            'author': self.author.username,
            'update_time': self.update_time.astimezone().strftime('%Y年%m月%d日 %H:%M'),
            'parent': self.parent.to_dict_data() if self.parent else None
        }
        return comment_dict


class HotNews(BaseModel):
    """
    推荐文章表：和文章表是一对一的关系
    """
    news = models.OneToOneField('News', on_delete=models.CASCADE)
    priority = models.IntegerField('优先级', help_text='优先级')

    class Meta:
        ordering = ['-update_time', '-id']                      # 排序
        db_table = "tb_hotnews"                                     # 数据库中表名
        verbose_name = "热门新闻"                               # 在admin站点中显示的名称
        verbose_name_plural = verbose_name                      # 显示的复数名称

    def __str__(self):
        return '<热门新闻{}>'.format(self.id)


class Banner(BaseModel):
    """
    轮播图
    """
    image_url = models.URLField('轮播图url', help_text='轮播图url')
    priority = models.IntegerField('优先级', help_text='优先级')

    news = models.OneToOneField('News', on_delete=models.CASCADE)

    class Meta:
        ordering = ['-update_time', '-id']                      # 排序
        db_table = "tb_banner"                                     # 数据库中表名
        verbose_name = "轮播图"                               # 在admin站点中显示的名称
        verbose_name_plural = verbose_name                      # 显示的复数名称

    def __str__(self):
        return '<轮播图{}>'.format(self.id)
from django.contrib.auth.models import User
from django.db import models


class Category(models.Model):
    """博客分类"""

    name = models.CharField(max_length=100, unique=True, verbose_name="分类名称")
    slug = models.SlugField(max_length=100, unique=True, verbose_name="URL 别名")

    class Meta:
        verbose_name = "分类"
        verbose_name_plural = "分类"

    def __str__(self):
        return self.name


class Blog(models.Model):
    """博客文章"""

    class Status(models.TextChoices):
        DRAFT = "draft", "草稿"
        PUBLISHED = "published", "已发布"

    title = models.CharField(max_length=200, verbose_name="标题")
    slug = models.SlugField(max_length=200, unique=True, verbose_name="URL 别名")
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="blogs", verbose_name="作者")
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL, null=True, blank=True, related_name="blogs", verbose_name="分类"
    )
    content = models.TextField(verbose_name="内容")
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.DRAFT, verbose_name="状态")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "博客文章"
        verbose_name_plural = "博客文章"
        indexes = [
            models.Index(fields=["-created_at"]),
        ]

    def __str__(self):
        return self.title

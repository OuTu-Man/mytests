from django.db import models


class AIPlatform(models.Model):
    name = models.CharField(max_length=200)
    open_ai_url = models.URLField()
    claude_code_url = models.URLField()
    other_url = models.URLField(blank=True, null=True)
    api_key = models.CharField(max_length=200, blank=True, default="", verbose_name="API Key")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class AiModels(models.Model):
    name = models.CharField(max_length=200)
    name_type = models.CharField(max_length=200)
    base_urls = models.ManyToManyField(AIPlatform, blank=True, related_name="ai_configs", verbose_name="关联的Base URL")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

from django import forms
from django.contrib import admin

from .models import AiModels, AIPlatform


def mask_api_key(value):
    """仅显示 API Key 前 4 个字符，其余以 **** 代替"""
    if not value:
        return "-"
    return f"{value[:4]}****"


class AIPlatformForm(forms.ModelForm):
    class Meta:
        model = AIPlatform
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 编辑已有记录时，输入框展示脱敏后的值
        # 注意：必须覆盖 self.initial（ModelForm 会把实例明文值放入其中），
        # 只设 field.initial 会被 self.initial 覆盖
        if self.instance.pk:
            self.initial["api_key"] = mask_api_key(self.instance.api_key)

    def clean_api_key(self):
        value = self.cleaned_data["api_key"]
        # 值未改动（仍是脱敏占位符）时，还原为数据库中的真实 Key
        if self.instance.pk and value == mask_api_key(self.instance.api_key):
            return self.instance.api_key
        return value


@admin.register(AIPlatform)
class AIPlatformAdmin(admin.ModelAdmin):
    form = AIPlatformForm
    list_display = ("id", "name", "open_ai_url", "masked_api_key", "created_at")

    @admin.display(description="API Key")
    def masked_api_key(self, obj):
        return mask_api_key(obj.api_key)


@admin.register(AiModels)
class AiModelAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "name_type", "created_at")
    filter_horizontal = ("base_urls",)  # 多选更好用

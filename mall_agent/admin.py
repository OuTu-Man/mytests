from django.contrib import admin

from .models import Conversation, Message


class MessageInline(admin.TabularInline):
    model = Message
    extra = 0
    readonly_fields = ("role", "content", "tool_name", "tool_args", "tool_result", "created_at")


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ("id", "user_id", "title", "created_at", "updated_at")
    inlines = [MessageInline]

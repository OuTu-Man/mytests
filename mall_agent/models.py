from django.db import models


class Conversation(models.Model):
    user_id = models.IntegerField(db_index=True)
    title = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Conv-{self.id}-user{self.user_id}"


class Message(models.Model):
    ROLE_CHOICES = [
        ("user", "用户"),
        ("assistant", "助手"),
        ("tool", "工具"),
        ("system", "系统"),
    ]
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name="messages")
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    content = models.TextField(blank=True)
    tool_name = models.CharField(max_length=100, blank=True)
    tool_args = models.JSONField(blank=True, null=True)
    tool_result = models.JSONField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["id"]

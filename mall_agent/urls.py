from django.urls import path

from .views import ChatView, ConversationListView

urlpatterns = [
    path("chat/", ChatView.as_view()),
    path("conversations/", ConversationListView.as_view()),
]

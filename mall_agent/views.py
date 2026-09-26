from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Conversation
from .serializers import ConversationSerializer, MessageSerializer
from .services import run_agent


class ChatView(APIView):
    def post(self, request):
        user_id = request.data.get("user_id")
        message = request.data.get("message", "").strip()
        conversation_id = request.data.get("conversation_id")

        if not user_id or not message:
            return Response(
                {"error": "user_id 和 message 必填"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if conversation_id:
            try:
                conv = Conversation.objects.get(id=conversation_id, user_id=user_id)
            except Conversation.DoesNotExist:
                return Response({"error": "会话不存在"}, status=404)
        else:
            conv = Conversation.objects.create(user_id=user_id, title=message[:30])

        reply = run_agent(conv, message, user_id)

        return Response(
            {
                "conversation_id": conv.id,
                "reply": reply,
                "messages": MessageSerializer(conv.messages.all(), many=True).data,
            }
        )


class ConversationListView(APIView):
    def get(self, request):
        user_id = request.query_params.get("user_id")
        qs = Conversation.objects.filter(user_id=user_id).order_by("-updated_at")
        return Response(ConversationSerializer(qs, many=True).data)

import json

from .llm import SYSTEM_PROMPT, chat
from .models import Conversation, Message
from .tools import TOOL_MAP, TOOLS


def run_agent(conversation: Conversation, user_input: str, user_id: int):
    # 1. 存用户消息
    Message.objects.create(conversation=conversation, role="user", content=user_input)

    # 2. 组装历史消息
    history = [{"role": "system", "content": SYSTEM_PROMPT}]
    for msg in conversation.messages.order_by("id"):
        if msg.role == "user":
            history.append({"role": "user", "content": msg.content})
        elif msg.role == "assistant" and msg.content:
            history.append({"role": "assistant", "content": msg.content})
        # tool 消息在下面单独处理

    # 3. 多轮 tool calling
    max_rounds = 5
    for _ in range(max_rounds):
        resp = chat(history, tools=TOOLS)

        # 没有工具调用 → 最终回答
        if not resp.tool_calls:
            content = resp.content or ""
            Message.objects.create(conversation=conversation, role="assistant", content=content)
            return content

        # 有工具调用
        history.append(
            {
                "role": "assistant",
                "content": resp.content or "",
                "tool_calls": [
                    {
                        "id": tc.id,
                        "type": "function",
                        "function": {
                            "name": tc.function.name,
                            "arguments": tc.function.arguments,
                        },
                    }
                    for tc in resp.tool_calls
                ],
            }
        )

        for tc in resp.tool_calls:
            name = tc.function.name
            args = json.loads(tc.function.arguments or "{}")

            # 注入 user_id，防止越权查别人订单
            if name in ("get_order_status", "get_logistics"):
                args["user_id"] = user_id

            func = TOOL_MAP.get(name)
            try:
                result = func(**args) if func else {"error": f"未知工具 {name}"}
            except Exception as e:
                result = {"error": str(e)}

            # 存工具调用记录
            Message.objects.create(
                conversation=conversation,
                role="tool",
                tool_name=name,
                tool_args=args,
                tool_result=result,
            )

            history.append(
                {
                    "role": "tool",
                    "tool_call_id": tc.id,
                    "content": json.dumps(result, ensure_ascii=False),
                }
            )

    return "抱歉，我暂时无法处理，请稍后再试。"

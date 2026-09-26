from openai import OpenAI

from agents.models import AIPlatform


def get_platform():
    """获取已配置的 AI 平台（当前取第一条记录）"""
    platform = AIPlatform.objects.first()
    if platform is None:
        raise RuntimeError("未配置 AI 平台，请先在 admin 的 AIPlatform 中添加")
    return platform


def get_client():
    """从 agents 应用读取 API Key 与 Base URL，构造 OpenAI 客户端"""
    platform = get_platform()
    return OpenAI(
        api_key=platform.api_key,
        base_url=platform.open_ai_url,
    )


def get_model(platform=None):
    """获取平台关联的第一个模型 ID"""
    platform = platform or get_platform()
    model = platform.ai_configs.first()
    if model is None:
        raise RuntimeError("平台未关联任何模型，请在 admin 的 AiModels 中配置")
    return model.name_type


SYSTEM_PROMPT = """你是一个商城客服助手，名叫小美。
你可以帮用户：搜索商品、推荐商品、查询订单状态、查询物流。
规则：
1. 涉及订单/物流，必须让用户提供订单号。
2. 不要编造商品、订单、物流信息，一切以工具返回为准。
3. 回答简洁友好，多用短句。
4. 用户问价格时，用人民币符号。
"""


def chat(messages, tools=None):
    """调用 LLM，返回 message 对象"""
    resp = get_client().chat.completions.create(
        model=get_model(),
        messages=messages,
        tools=tools,
        tool_choice="auto" if tools else None,
        temperature=0.3,
    )
    return resp.choices[0].message

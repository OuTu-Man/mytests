from mall.models import Logistics, Order, Product


def search_products(keyword: str, max_price: float | None = None, limit: int = 5):
    """按关键词搜索商品"""
    qs = Product.objects.filter(is_active=True, name__icontains=keyword)
    if max_price:
        qs = qs.filter(price__lte=max_price)
    qs = qs[:limit]
    return [
        {
            "id": p.id,
            "name": p.name,
            "price": float(p.price),
            "stock": p.stock,
            "description": p.description[:100],
        }
        for p in qs
    ]


def get_order_status(order_no: str, user_id: int):
    """查询订单状态"""
    try:
        order = Order.objects.get(order_no=order_no, user_id=user_id)
    except Order.DoesNotExist:
        return {"error": "未找到该订单，请确认订单号是否正确"}

    return {
        "order_no": order.order_no,
        "status": order.get_status_display(),
        "total_amount": float(order.total_amount),
        "created_at": order.created_at.strftime("%Y-%m-%d %H:%M"),
        "items": [
            {
                "product": item.product.name,
                "quantity": item.quantity,
                "price": float(item.price),
            }
            for item in order.items.all()
        ],
    }


def get_logistics(order_no: str, user_id: int):
    """查询物流"""
    try:
        order = Order.objects.get(order_no=order_no, user_id=user_id)
        logistics = order.logistics
    except Order.DoesNotExist, Logistics.DoesNotExist:
        return {"error": "暂无物流信息"}

    return {
        "company": logistics.company,
        "tracking_no": logistics.tracking_no,
        "latest_info": logistics.latest_info,
        "updated_at": logistics.updated_at.strftime("%Y-%m-%d %H:%M"),
    }


def recommend_products(category: str | None = None, limit: int = 5):
    """推荐商品"""
    qs = Product.objects.filter(is_active=True, stock__gt=0)
    if category:
        qs = qs.filter(category=category)
    qs = qs.order_by("-id")[:limit]
    return [{"id": p.id, "name": p.name, "price": float(p.price)} for p in qs]


# 工具注册表：给 LLM 看的定义
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "search_products",
            "description": "按关键词搜索商品，可限制最高价格",
            "parameters": {
                "type": "object",
                "properties": {
                    "keyword": {"type": "string", "description": "搜索关键词"},
                    "max_price": {"type": "number", "description": "最高价格"},
                },
                "required": ["keyword"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_order_status",
            "description": "根据订单号查询订单状态",
            "parameters": {
                "type": "object",
                "properties": {
                    "order_no": {"type": "string", "description": "订单号"},
                },
                "required": ["order_no"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_logistics",
            "description": "根据订单号查询物流信息",
            "parameters": {
                "type": "object",
                "properties": {
                    "order_no": {"type": "string", "description": "订单号"},
                },
                "required": ["order_no"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "recommend_products",
            "description": "推荐商品，可按分类",
            "parameters": {
                "type": "object",
                "properties": {
                    "category": {"type": "string", "description": "商品分类"},
                },
            },
        },
    },
]

# 工具名 → 函数映射
TOOL_MAP = {
    "search_products": search_products,
    "get_order_status": get_order_status,
    "get_logistics": get_logistics,
    "recommend_products": recommend_products,
}

import hashlib
import json
import os
from datetime import datetime

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url=os.getenv("OPENAI_BASE_URL"),
)

# ==================== 模拟数据库 ====================

ORDERS = {
    "SO20260101001": {
        "user_id": "U1001",
        "product": "无线蓝牙耳机 Pro",
        "sku": "SKU-EAR-001",
        "amount": 299.00,
        "status": "已发货",
        "pay_time": "2026-01-01 10:23:00",
        "express": "顺丰速运",
        "tracking_no": "SF1234567890",
        "address": "广东省深圳市南山区科技园",
    },
    "SO20260102002": {
        "user_id": "U1001",
        "product": "机械键盘 K8",
        "sku": "SKU-KB-008",
        "amount": 499.00,
        "status": "待发货",
        "pay_time": "2026-01-02 14:05:00",
        "express": None,
        "tracking_no": None,
        "address": "广东省深圳市南山区科技园",
    },
    "SO20260103003": {
        "user_id": "U1002",
        "product": "智能手表 S2",
        "sku": "SKU-WATCH-002",
        "amount": 1299.00,
        "status": "已完成",
        "pay_time": "2025-12-20 09:00:00",
        "express": "京东物流",
        "tracking_no": "JD9876543210",
        "address": "北京市朝阳区建国路",
    },
}

SHIPPING = {
    "SF1234567890": {
        "company": "顺丰速运",
        "status": "运输中",
        "latest": "2026-01-03 08:30 已到达深圳南山集散中心",
        "traces": [
            "2026-01-01 18:00 快件已揽收",
            "2026-01-02 06:00 已发往深圳",
            "2026-01-03 08:30 已到达深圳南山集散中心",
        ],
    },
    "JD9876543210": {
        "company": "京东物流",
        "status": "已签收",
        "latest": "2025-12-23 15:20 已签收，感谢使用",
        "traces": [
            "2025-12-21 10:00 已出库",
            "2025-12-22 09:00 配送中",
            "2025-12-23 15:20 已签收",
        ],
    },
}

PRODUCTS = {
    "SKU-EAR-001": {"name": "无线蓝牙耳机 Pro", "price": 299, "stock": 150, "warranty": "1年"},
    "SKU-KB-008": {"name": "机械键盘 K8", "price": 499, "stock": 80, "warranty": "1年"},
    "SKU-WATCH-002": {"name": "智能手表 S2", "price": 1299, "stock": 30, "warranty": "2年"},
}

POLICIES = {
    "退货": "支持 7 天无理由退货，商品需保持完好、不影响二次销售。",
    "换货": "支持 15 天质量问题换货，需提供照片或视频凭证。",
    "退款": "退款将在审核通过后 1-3 个工作日原路退回。",
    "运费": "满 99 元包邮，偏远地区（新疆、西藏等）需补运费。",
    "保修": "电子产品保修 1-2 年，人为损坏不在保修范围内。",
    "发票": "支持开具电子发票，可在订单详情页申请。",
}

COUPONS = {
    "U1001": [
        {"code": "NEW50", "desc": "新人满 200 减 50", "expire": "2026-02-01"},
        {"code": "VIP10", "desc": "会员 9 折券", "expire": "2026-03-01"},
    ],
    "U1002": [
        {"code": "FREESHIP", "desc": "免运费券", "expire": "2026-01-31"},
    ],
}

TICKETS = []


# ==================== 工具函数 ====================


def query_order(order_id: str) -> str:
    """根据订单号查询订单详情"""
    order = ORDERS.get(order_id)
    if not order:
        return f"未找到订单 {order_id}，请确认订单号是否正确。"
    return json.dumps(
        {
            "订单号": order_id,
            "商品": order["product"],
            "金额": f"{order['amount']}元",
            "状态": order["status"],
            "下单时间": order["pay_time"],
            "收货地址": order["address"],
        },
        ensure_ascii=False,
    )


def track_shipping(order_id: str) -> str:
    """根据订单号查询物流轨迹"""
    order = ORDERS.get(order_id)
    if not order:
        return f"未找到订单 {order_id}。"
    tracking_no = order.get("tracking_no")
    if not tracking_no:
        return f"订单 {order_id} 尚未发货，暂无物流信息。"
    info = SHIPPING.get(tracking_no)
    if not info:
        return f"物流单号 {tracking_no} 暂无轨迹信息。"
    return json.dumps(
        {
            "快递公司": info["company"],
            "当前状态": info["status"],
            "最新动态": info["latest"],
            "完整轨迹": info["traces"],
        },
        ensure_ascii=False,
    )


def query_product(sku: str) -> str:
    """根据 SKU 查询商品信息"""
    product = PRODUCTS.get(sku)
    if not product:
        return f"未找到商品 {sku}。"
    return json.dumps(
        {
            "商品名称": product["name"],
            "价格": f"{product['price']}元",
            "库存": product["stock"],
            "保修": product["warranty"],
        },
        ensure_ascii=False,
    )


def search_policy(query: str) -> str:
    """检索售后政策知识库"""
    for key, value in POLICIES.items():
        if key in query:
            return f"【{key}政策】{value}"
    return "未找到相关政策，建议转人工咨询。"


def apply_return(order_id: str, reason: str) -> str:
    """申请退货/换货"""
    order = ORDERS.get(order_id)
    if not order:
        return f"未找到订单 {order_id}，无法申请售后。"
    if order["status"] not in ("已发货", "已完成"):
        return f"订单 {order_id} 当前状态为「{order['status']}」，暂不支持申请售后。"
    ticket_id = f"RT{hashlib.md5(f'{order_id}{reason}'.encode()).hexdigest()[:8].upper()}"
    return json.dumps(
        {
            "售后单号": ticket_id,
            "订单号": order_id,
            "类型": "退货",
            "原因": reason,
            "状态": "已提交，等待审核",
            "提示": "审核通过后请将商品寄回，运费由我方承担。",
        },
        ensure_ascii=False,
    )


def apply_refund(order_id: str, reason: str) -> str:
    """申请退款"""
    order = ORDERS.get(order_id)
    if not order:
        return f"未找到订单 {order_id}。"
    if order["status"] == "已完成":
        return f"订单 {order_id} 已完成，请先申请退货，退货签收后退款将自动原路退回。"
    refund_id = f"RF{hashlib.md5(f'{order_id}{reason}'.encode()).hexdigest()[:8].upper()}"
    return json.dumps(
        {
            "退款单号": refund_id,
            "订单号": order_id,
            "退款金额": f"{order['amount']}元",
            "状态": "已提交，1-3 个工作日原路退回",
        },
        ensure_ascii=False,
    )


def query_coupons(user_id: str) -> str:
    """查询用户优惠券"""
    coupons = COUPONS.get(user_id, [])
    if not coupons:
        return f"用户 {user_id} 暂无可用优惠券。"
    return json.dumps(coupons, ensure_ascii=False)


def create_ticket(issue: str, user_id: str = "anonymous", order_id: str = "") -> str:
    """创建人工工单"""
    ticket_id = f"TK{len(TICKETS) + 10001}"
    TICKETS.append(
        {
            "ticket_id": ticket_id,
            "user_id": user_id,
            "order_id": order_id,
            "issue": issue,
            "status": "待处理",
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }
    )
    return json.dumps(
        {
            "工单号": ticket_id,
            "问题": issue,
            "状态": "已创建，客服将在 24 小时内联系您",
        },
        ensure_ascii=False,
    )


def transfer_to_human(reason: str) -> str:
    """转接人工客服"""
    return f"正在为您转接人工客服（原因：{reason}），请稍候。当前排队人数：3 人，预计等待 2 分钟。"


# ==================== 工具注册表 ====================

TOOLS = {
    "query_order": (query_order, "查询订单详情，参数 order_id"),
    "track_shipping": (track_shipping, "查询物流轨迹，参数 order_id"),
    "query_product": (query_product, "查询商品信息，参数 sku"),
    "search_policy": (search_policy, "检索售后政策，参数 query"),
    "apply_return": (apply_return, "申请退货/换货，参数 order_id, reason"),
    "apply_refund": (apply_refund, "申请退款，参数 order_id, reason"),
    "query_coupons": (query_coupons, "查询用户优惠券，参数 user_id"),
    "create_ticket": (create_ticket, "创建工单，参数 issue, user_id(可选), order_id(可选)"),
    "transfer_to_human": (transfer_to_human, "转人工，参数 reason"),
}

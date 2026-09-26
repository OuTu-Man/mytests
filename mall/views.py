from rest_framework import generics

from .models import Order, Product
from .serializers import OrderSerializer, ProductSerializer


class ProductListCreateView(generics.ListCreateAPIView):
    """商品列表 / 新建商品"""

    queryset = Product.objects.filter(is_active=True)
    serializer_class = ProductSerializer


class ProductDetailView(generics.RetrieveUpdateDestroyAPIView):
    """商品详情 / 更新 / 删除"""

    queryset = Product.objects.all()
    serializer_class = ProductSerializer


class OrderListCreateView(generics.ListCreateAPIView):
    """订单列表（按 user_id 过滤）/ 新建订单"""

    serializer_class = OrderSerializer

    def get_queryset(self):
        user_id = self.request.query_params.get("user_id")
        return Order.objects.filter(user_id=user_id)


class OrderDetailView(generics.RetrieveAPIView):
    """订单详情，仅能查看本人订单（需传 user_id）"""

    serializer_class = OrderSerializer

    def get_queryset(self):
        user_id = self.request.query_params.get("user_id")
        return Order.objects.filter(user_id=user_id)

from django.contrib import admin

from .models import Logistics, Order, OrderItem, Product


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "price", "stock", "category", "is_active", "created_at")
    list_filter = ("is_active", "category", "created_at")
    search_fields = ("name", "description")
    list_editable = ("price", "stock", "is_active")


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ("product", "quantity", "price")


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "order_no", "user_id", "status", "total_amount", "created_at")
    list_filter = ("status", "created_at")
    search_fields = ("order_no",)
    inlines = [OrderItemInline]


@admin.register(Logistics)
class LogisticsAdmin(admin.ModelAdmin):
    list_display = ("id", "order", "company", "tracking_no", "updated_at")
    search_fields = ("tracking_no", "company")

from django.contrib import admin
from .models import Product, Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['product', 'quantity', 'price_at_purchase']


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'price']
    search_fields = ['name']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'status', 'total', 'created_at']
    list_filter = ['status']
    readonly_fields = ['id', 'stripe_session_id', 'created_at', 'updated_at']
    inlines = [OrderItemInline]

    def total(self, obj):
        return f"${obj.total:.2f}"

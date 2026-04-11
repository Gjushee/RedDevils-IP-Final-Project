from django.contrib import admin
from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('product_name', 'size', 'quantity', 'unit_price')


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display  = ('order_ref', 'user', 'status', 'payment_method', 'total_amount', 'created_at')
    list_filter   = ('status', 'payment_method')
    search_fields = ('order_ref', 'user__username', 'email')
    readonly_fields = ('order_ref', 'created_at')
    inlines = [OrderItemInline]

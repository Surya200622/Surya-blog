from django.contrib import admin
from .models import Plan, Order, Payment, Subscription


@admin.register(Plan)
class PlanAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'duration_days', 'is_popular', 'is_active', 'order']
    list_editable = ['price', 'is_popular', 'is_active', 'order']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_id', 'user', 'plan', 'amount', 'status', 'razorpay_order_id', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['order_id', 'user__username', 'razorpay_order_id']
    readonly_fields = ['order_id', 'razorpay_order_id']


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['razorpay_payment_id', 'order', 'amount', 'method', 'status', 'verified_at']
    list_filter = ['status', 'method', 'created_at']
    search_fields = ['razorpay_payment_id']
    readonly_fields = ['razorpay_payment_id', 'razorpay_signature', 'verified_at']


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ['user', 'plan', 'starts_at', 'expires_at', 'is_active', 'days_remaining']
    list_filter = ['is_active', 'plan']
    search_fields = ['user__username']

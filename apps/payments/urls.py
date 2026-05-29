from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    path('pricing/', views.PricingView.as_view(), name='pricing'),
    path('checkout/<slug:slug>/', views.CheckoutView.as_view(), name='checkout'),
    path('create-order/', views.CreateOrderView.as_view(), name='create_order'),
    path('verify/', views.VerifyPaymentView.as_view(), name='verify'),
    path('success/<uuid:order_id>/', views.PaymentSuccessView.as_view(), name='success'),
    path('history/', views.PaymentHistoryView.as_view(), name='history'),
    path('webhook/', views.RazorpayWebhookView.as_view(), name='webhook'),
]

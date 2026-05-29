from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponseBadRequest
from django.utils import timezone
from django.conf import settings
from datetime import timedelta
import json
import logging

from .models import Plan, Order, Payment, Subscription
from .utils import create_razorpay_order, verify_razorpay_signature, fetch_payment_details

logger = logging.getLogger(__name__)


class PricingView(View):
    """Display pricing plans."""

    def get(self, request):
        plans = Plan.objects.filter(is_active=True)
        context = {
            'plans': plans,
            'page_title': 'Pricing Plans',
            'meta_description': 'Choose the perfect plan for your needs. Start creating amazing content today.',
        }
        return render(request, 'payments/pricing.html', context)


@method_decorator(login_required, name='dispatch')
class CheckoutView(View):
    """Checkout page for a specific plan."""

    def get(self, request, slug):
        plan = get_object_or_404(Plan, slug=slug, is_active=True)
        context = {
            'plan': plan,
            'razorpay_key_id': settings.RAZORPAY_KEY_ID,
            'page_title': f'Checkout — {plan.name}',
        }
        return render(request, 'payments/checkout.html', context)


@method_decorator(login_required, name='dispatch')
class CreateOrderView(View):
    """Create Razorpay order (AJAX endpoint)."""

    def post(self, request):
        try:
            data = json.loads(request.body)
            plan_slug = data.get('plan_slug')
        except (json.JSONDecodeError, KeyError):
            return JsonResponse({'error': 'Invalid request'}, status=400)

        plan = get_object_or_404(Plan, slug=plan_slug, is_active=True)

        # Create internal order
        order = Order.objects.create(
            user=request.user,
            plan=plan,
            amount=plan.price,
            description=f'{plan.name} — {plan.description}',
        )

        # Create Razorpay order
        razorpay_order = create_razorpay_order(
            amount_inr=plan.price,
            receipt=str(order.order_id),
            notes={
                'plan': plan.name,
                'user': request.user.username,
            }
        )

        if not razorpay_order:
            order.status = 'failed'
            order.save()
            return JsonResponse({'error': 'Failed to create payment order'}, status=500)

        # Save Razorpay order ID
        order.razorpay_order_id = razorpay_order['id']
        order.save()

        return JsonResponse({
            'order_id': razorpay_order['id'],
            'amount': razorpay_order['amount'],
            'currency': razorpay_order['currency'],
            'key_id': settings.RAZORPAY_KEY_ID,
            'name': settings.SITE_NAME,
            'description': plan.name,
            'prefill': {
                'name': request.user.get_full_name() or request.user.username,
                'email': request.user.email,
            }
        })


@method_decorator(login_required, name='dispatch')
class VerifyPaymentView(View):
    """Verify Razorpay payment after checkout."""

    def post(self, request):
        try:
            data = json.loads(request.body)
            razorpay_order_id = data.get('razorpay_order_id')
            razorpay_payment_id = data.get('razorpay_payment_id')
            razorpay_signature = data.get('razorpay_signature')
        except (json.JSONDecodeError, KeyError):
            return JsonResponse({'error': 'Invalid request'}, status=400)

        if not all([razorpay_order_id, razorpay_payment_id, razorpay_signature]):
            return JsonResponse({'error': 'Missing payment data'}, status=400)

        # Verify signature
        is_valid = verify_razorpay_signature(
            razorpay_order_id, razorpay_payment_id, razorpay_signature
        )

        if not is_valid:
            return JsonResponse({'error': 'Payment verification failed'}, status=400)

        # Update order
        try:
            order = Order.objects.get(razorpay_order_id=razorpay_order_id, user=request.user)
        except Order.DoesNotExist:
            return JsonResponse({'error': 'Order not found'}, status=404)

        order.status = 'paid'
        order.save()

        # Fetch payment details from Razorpay
        payment_details = fetch_payment_details(razorpay_payment_id)

        # Create payment record
        payment = Payment.objects.create(
            order=order,
            razorpay_payment_id=razorpay_payment_id,
            razorpay_signature=razorpay_signature,
            method=payment_details.get('method', '') if payment_details else '',
            amount=order.amount,
            status='captured',
            verified_at=timezone.now(),
        )

        # Create subscription if plan exists
        if order.plan:
            Subscription.objects.create(
                user=request.user,
                plan=order.plan,
                order=order,
                starts_at=timezone.now(),
                expires_at=timezone.now() + timedelta(days=order.plan.duration_days),
                is_active=True,
            )

        return JsonResponse({
            'success': True,
            'payment_id': razorpay_payment_id,
            'redirect_url': f'/payments/success/{order.order_id}/',
        })


@method_decorator(login_required, name='dispatch')
class PaymentSuccessView(View):
    """Payment success page."""

    def get(self, request, order_id):
        order = get_object_or_404(Order, order_id=order_id, user=request.user)
        payment = getattr(order, 'payment', None)

        context = {
            'order': order,
            'payment': payment,
            'page_title': 'Payment Successful',
        }
        return render(request, 'payments/success.html', context)


@method_decorator(login_required, name='dispatch')
class PaymentHistoryView(View):
    """User's payment history."""

    def get(self, request):
        orders = Order.objects.filter(user=request.user).order_by('-created_at')

        context = {
            'orders': orders,
            'page_title': 'Payment History',
        }
        return render(request, 'payments/history.html', context)


@method_decorator(csrf_exempt, name='dispatch')
class RazorpayWebhookView(View):
    """Handle Razorpay webhook callbacks."""

    def post(self, request):
        try:
            payload = json.loads(request.body)
            event = payload.get('event')

            if event == 'payment.captured':
                payment_entity = payload['payload']['payment']['entity']
                order_id = payment_entity.get('order_id')

                try:
                    order = Order.objects.get(razorpay_order_id=order_id)
                    order.status = 'paid'
                    order.save()
                    logger.info(f"Webhook: Order {order_id} marked as paid")
                except Order.DoesNotExist:
                    logger.warning(f"Webhook: Order {order_id} not found")

            elif event == 'payment.failed':
                payment_entity = payload['payload']['payment']['entity']
                order_id = payment_entity.get('order_id')

                try:
                    order = Order.objects.get(razorpay_order_id=order_id)
                    order.status = 'failed'
                    order.save()
                    logger.info(f"Webhook: Order {order_id} marked as failed")
                except Order.DoesNotExist:
                    logger.warning(f"Webhook: Order {order_id} not found")

            return JsonResponse({'status': 'ok'})

        except Exception as e:
            logger.error(f"Webhook error: {e}")
            return JsonResponse({'status': 'error'}, status=500)

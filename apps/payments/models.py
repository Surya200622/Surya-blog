from django.db import models
from django.conf import settings
import uuid


class Plan(models.Model):
    """Subscription/service plan for payments."""

    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, help_text='Price in INR')
    duration_days = models.IntegerField(default=30, help_text='Plan duration in days')
    features = models.JSONField(default=list, blank=True, help_text='List of plan features')
    is_popular = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order', 'price']

    def __str__(self):
        return f'{self.name} — ₹{self.price}'


class Order(models.Model):
    """Payment order linked to Razorpay."""

    class Status(models.TextChoices):
        CREATED = 'created', 'Created'
        PAID = 'paid', 'Paid'
        FAILED = 'failed', 'Failed'
        REFUNDED = 'refunded', 'Refunded'

    order_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='orders',
    )
    plan = models.ForeignKey(
        Plan,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='orders',
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='INR')
    razorpay_order_id = models.CharField(max_length=100, blank=True)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.CREATED,
    )
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'Order #{self.order_id} — ₹{self.amount} ({self.status})'

    @property
    def amount_in_paise(self):
        """Razorpay expects amounts in paise (smallest currency unit)."""
        return int(self.amount * 100)


class Payment(models.Model):
    """Verified payment record from Razorpay."""

    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        CAPTURED = 'captured', 'Captured'
        FAILED = 'failed', 'Failed'
        REFUNDED = 'refunded', 'Refunded'

    order = models.OneToOneField(
        Order,
        on_delete=models.CASCADE,
        related_name='payment',
    )
    razorpay_payment_id = models.CharField(max_length=100)
    razorpay_signature = models.CharField(max_length=256, blank=True)
    method = models.CharField(max_length=50, blank=True, help_text='UPI, card, netbanking, etc.')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='INR')
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
    )
    verified_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'Payment {self.razorpay_payment_id} — ₹{self.amount}'


class Subscription(models.Model):
    """User subscription to a plan."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='subscriptions',
    )
    plan = models.ForeignKey(Plan, on_delete=models.CASCADE, related_name='subscriptions')
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True)
    starts_at = models.DateTimeField()
    expires_at = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    auto_renew = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.user.username} — {self.plan.name}'

    @property
    def is_expired(self):
        from django.utils import timezone
        return timezone.now() > self.expires_at

    @property
    def days_remaining(self):
        from django.utils import timezone
        if self.is_expired:
            return 0
        return (self.expires_at - timezone.now()).days

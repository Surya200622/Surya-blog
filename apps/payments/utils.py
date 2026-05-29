"""
Razorpay utility functions.
"""
import razorpay
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


def get_razorpay_client():
    """Initialize and return Razorpay client."""
    return razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))


def create_razorpay_order(amount_inr, currency='INR', receipt=None, notes=None):
    """
    Create a Razorpay order.

    Args:
        amount_inr: Amount in INR (will be converted to paise)
        currency: Currency code (default: INR)
        receipt: Order receipt ID
        notes: Additional notes dict

    Returns:
        Razorpay order object or None on failure
    """
    client = get_razorpay_client()

    order_data = {
        'amount': int(float(amount_inr) * 100),  # Convert to paise
        'currency': currency,
        'payment_capture': '1',  # Auto capture
    }

    if receipt:
        order_data['receipt'] = str(receipt)
    if notes:
        order_data['notes'] = notes

    try:
        order = client.order.create(data=order_data)
        logger.info(f"Razorpay order created: {order['id']}")
        return order
    except Exception as e:
        logger.error(f"Failed to create Razorpay order: {e}")
        return None


def verify_razorpay_signature(razorpay_order_id, razorpay_payment_id, razorpay_signature):
    """
    Verify Razorpay payment signature for authenticity.

    Returns:
        True if signature is valid, False otherwise
    """
    client = get_razorpay_client()

    params_dict = {
        'razorpay_order_id': razorpay_order_id,
        'razorpay_payment_id': razorpay_payment_id,
        'razorpay_signature': razorpay_signature,
    }

    try:
        client.utility.verify_payment_signature(params_dict)
        logger.info(f"Payment signature verified: {razorpay_payment_id}")
        return True
    except razorpay.errors.SignatureVerificationError:
        logger.warning(f"Invalid payment signature: {razorpay_payment_id}")
        return False


def fetch_payment_details(payment_id):
    """Fetch payment details from Razorpay."""
    client = get_razorpay_client()
    try:
        return client.payment.fetch(payment_id)
    except Exception as e:
        logger.error(f"Failed to fetch payment {payment_id}: {e}")
        return None


def create_refund(payment_id, amount_inr=None):
    """
    Create a refund for a payment.

    Args:
        payment_id: Razorpay payment ID
        amount_inr: Partial refund amount in INR (None for full refund)
    """
    client = get_razorpay_client()
    refund_data = {}
    if amount_inr:
        refund_data['amount'] = int(float(amount_inr) * 100)

    try:
        refund = client.payment.refund(payment_id, refund_data)
        logger.info(f"Refund created for payment {payment_id}")
        return refund
    except Exception as e:
        logger.error(f"Failed to create refund for {payment_id}: {e}")
        return None

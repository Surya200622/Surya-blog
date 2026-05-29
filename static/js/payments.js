/* ═══════════════════════════════════════════════
   BlogCraft — Razorpay Payment Handler
   ═══════════════════════════════════════════════ */

function initPayment(planSlug) {
    const csrfToken = getCookie('csrftoken');

    // Show loading
    const payBtn = document.getElementById('pay-btn');
    if (payBtn) {
        payBtn.disabled = true;
        payBtn.innerHTML = '<span class="animate-spin">⏳</span> Processing...';
    }

    // Step 1: Create order on backend
    fetch('/payments/create-order/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken,
        },
        body: JSON.stringify({ plan_slug: planSlug }),
    })
    .then(res => res.json())
    .then(data => {
        if (data.error) {
            alert('Error: ' + data.error);
            resetPayButton();
            return;
        }

        // Step 2: Open Razorpay Checkout
        const options = {
            key: data.key_id,
            amount: data.amount,
            currency: data.currency,
            name: data.name,
            description: data.description,
            order_id: data.order_id,
            prefill: data.prefill,
            theme: {
                color: '#7c6cf0',
            },
            // UPI is automatically available in Razorpay Checkout
            handler: function(response) {
                // Step 3: Verify payment on backend
                verifyPayment(response);
            },
            modal: {
                ondismiss: function() {
                    resetPayButton();
                }
            }
        };

        const rzp = new Razorpay(options);
        rzp.on('payment.failed', function(response) {
            alert('Payment failed. Please try again.');
            console.error('Payment failed:', response.error);
            resetPayButton();
        });
        rzp.open();
    })
    .catch(err => {
        console.error('Order creation error:', err);
        alert('Something went wrong. Please try again.');
        resetPayButton();
    });
}

function verifyPayment(response) {
    const csrfToken = getCookie('csrftoken');

    fetch('/payments/verify/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken,
        },
        body: JSON.stringify({
            razorpay_order_id: response.razorpay_order_id,
            razorpay_payment_id: response.razorpay_payment_id,
            razorpay_signature: response.razorpay_signature,
        }),
    })
    .then(res => res.json())
    .then(data => {
        if (data.success) {
            // Redirect to success page
            window.location.href = data.redirect_url;
        } else {
            alert('Payment verification failed: ' + (data.error || 'Unknown error'));
            resetPayButton();
        }
    })
    .catch(err => {
        console.error('Verification error:', err);
        alert('Payment verification failed. Contact support.');
        resetPayButton();
    });
}

function resetPayButton() {
    const payBtn = document.getElementById('pay-btn');
    if (payBtn) {
        payBtn.disabled = false;
        payBtn.innerHTML = '💳 Pay Now';
    }
}

function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(';').shift();
    return '';
}

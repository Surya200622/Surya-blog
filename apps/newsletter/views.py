from django.http import HttpResponse
from django.views.decorators.http import require_POST
from .models import Subscriber
import re

@require_POST
def subscribe(request):
    email = request.POST.get('email', '').strip()
    
    # Basic validation
    if not email or not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        return HttpResponse('<div class="alert alert-error" style="font-size: 0.9rem; padding: 0.5rem; margin-top: 0.5rem;">Please enter a valid email.</div>')
    
    # Check if exists
    subscriber, created = Subscriber.objects.get_or_create(email=email)
    
    if created:
        return HttpResponse('<div class="alert alert-success" style="font-size: 0.9rem; padding: 0.5rem; margin-top: 0.5rem;">Thanks for subscribing! 🎉</div>')
    else:
        return HttpResponse('<div class="alert alert-info" style="font-size: 0.9rem; padding: 0.5rem; margin-top: 0.5rem;">You are already subscribed. 👍</div>')

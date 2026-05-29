"""
SEO context processors for template-level access.
"""
from django.conf import settings


def seo_context(request):
    """Add site-wide SEO data to template context."""
    return {
        'site_name': getattr(settings, 'SITE_NAME', 'BlogCraft'),
        'site_url': getattr(settings, 'SITE_URL', ''),
    }

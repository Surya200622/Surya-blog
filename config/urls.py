"""
Root URL Configuration for BlogCraft.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.sitemaps.views import sitemap
from django.views.generic import TemplateView
from apps.seo.sitemaps import PostSitemap, CategorySitemap, StaticViewSitemap

sitemaps = {
    'posts': PostSitemap,
    'categories': CategorySitemap,
    'static': StaticViewSitemap,
}

def custom_sitemap(request, sitemaps, **kwargs):
    response = sitemap(request, sitemaps, **kwargs)
    if hasattr(response, 'render'):
        response.render()
        content = response.content.decode('utf-8')
        domain = request.build_absolute_uri('/')[:-1]
        content = content.replace('http://example.com', domain).replace('https://example.com', domain)
        response.content = content.encode('utf-8')
    return response

from django.http import HttpResponse

def robots_txt(request):
    lines = [
        "User-agent: *",
        "Disallow: /admin/",
        "Disallow: /accounts/",
        "Disallow: /dashboard/",
        "Disallow: /payments/",
        "Allow: /",
        "",
        f"Sitemap: {request.build_absolute_uri('/')[:-1]}/sitemap.xml",
    ]
    return HttpResponse("\n".join(lines), content_type="text/plain")

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),

    # Auth (allauth)
    path('accounts/', include('apps.accounts.urls')),
    path('accounts/', include('allauth.urls')),

    # Blog
    path('blog/', include('apps.blog.urls')),

    # Dashboard
    path('dashboard/', include('apps.dashboard.urls')),

    # Payments
    path('payments/', include('apps.payments.urls')),

    # Freelance
    path('freelance/', include('apps.freelance.urls')),

    # Newsletter
    path('newsletter/', include('apps.newsletter.urls')),

    # CKEditor 5
    path('ckeditor5/', include('django_ckeditor_5.urls')),

    # SEO
    path('sitemap.xml', custom_sitemap, {'sitemaps': sitemaps, 'template_name': 'sitemap.xml'}, name='django.contrib.sitemaps.views.sitemap'),
    path('robots.txt', robots_txt, name='robots_txt'),

    # Pages (home, about, contact) — keep last for catch-all
    path('', include('apps.pages.urls')),
]

# Serve media files (needed for PythonAnywhere and local dev)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

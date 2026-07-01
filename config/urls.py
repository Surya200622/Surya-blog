"""
Root URL Configuration for BlogCraft.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.sitemaps.views import sitemap
from django.views.generic import TemplateView
from apps.seo.sitemaps import PostSitemap, CategorySitemap, StaticViewSitemap, ProjectSitemap

sitemaps = {
    'posts': PostSitemap,
    'categories': CategorySitemap,
    'static': StaticViewSitemap,
    'projects': ProjectSitemap,
}

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
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
    path('robots.txt', TemplateView.as_view(template_name='robots.txt', content_type='text/plain')),

    # Pages (home, about, contact) — keep last for catch-all
    path('', include('apps.pages.urls')),
]

# Serve media files (needed for PythonAnywhere and local dev)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

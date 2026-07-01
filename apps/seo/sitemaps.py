from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from apps.blog.models import Post, Category
from apps.freelance.models import Project


class PostSitemap(Sitemap):
    changefreq = 'weekly'
    priority = 0.8

    def items(self):
        return Post.objects.filter(status='published')

    def lastmod(self, obj):
        return obj.updated_at

    def location(self, obj):
        return obj.get_absolute_url()


class CategorySitemap(Sitemap):
    changefreq = 'monthly'
    priority = 0.6

    def items(self):
        return Category.objects.all()

    def location(self, obj):
        return obj.get_absolute_url()


class ProjectSitemap(Sitemap):
    changefreq = 'weekly'
    priority = 0.7

    def items(self):
        return Project.objects.filter(status='open')

    def lastmod(self, obj):
        return obj.updated_at

    def location(self, obj):
        return obj.get_absolute_url()


class StaticViewSitemap(Sitemap):
    changefreq = 'monthly'
    priority = 0.5

    def items(self):
        return ['pages:home', 'pages:about', 'pages:contact', 'blog:post_list', 'freelance:project_list']

    def location(self, item):
        return reverse(item)

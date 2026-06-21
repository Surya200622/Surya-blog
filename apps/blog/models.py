from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from django.conf import settings
from django_ckeditor_5.fields import CKEditor5Field
import math
import re


class PostSeries(models.Model):
    """A series of related blog posts."""
    name = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(max_length=200, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Series"

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Category(models.Model):
    """Blog post category with optional hierarchy."""

    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, blank=True, help_text='Lucide icon name, e.g. "code"')
    color = models.CharField(max_length=7, default='#6c5ce7', help_text='Hex color code')
    parent = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='children',
    )
    order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'
        ordering = ['order', 'name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('blog:category', kwargs={'slug': self.slug})

    @property
    def post_count(self):
        return self.posts.filter(status='published').count()


class Tag(models.Model):
    """Tag for blog posts."""

    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=50, unique=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('blog:tag', kwargs={'slug': self.slug})


class Post(models.Model):
    """Blog post with rich text content and SEO fields."""

    class Status(models.TextChoices):
        DRAFT = 'draft', 'Draft'
        PUBLISHED = 'published', 'Published'
        SCHEDULED = 'scheduled', 'Scheduled'
        ARCHIVED = 'archived', 'Archived'

    # Core fields
    title = models.CharField(max_length=250, verbose_name='Post Title')
    slug = models.SlugField(max_length=250, unique=True)
    content = CKEditor5Field(config_name='full', verbose_name='Content')
    excerpt = models.TextField(max_length=500, blank=True, verbose_name='Excerpt')
    featured_image = models.ImageField(
        upload_to='posts/%Y/%m/',
        blank=True,
        null=True,
        verbose_name='Featured Image',
    )

    # Relationships
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='blog_posts',
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='posts',
    )
    tags = models.ManyToManyField(Tag, blank=True, related_name='posts')
    series = models.ForeignKey(
        PostSeries,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='posts'
    )
    series_order = models.PositiveIntegerField(default=0, help_text="Order in the series")

    # Status & visibility
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.DRAFT,
    )
    is_premium = models.BooleanField(default=False, verbose_name='Premium Content')
    is_featured = models.BooleanField(default=False, verbose_name='Featured Post')
    is_project = models.BooleanField(default=False, verbose_name='Is Portfolio Project')

    # Metrics
    views_count = models.PositiveIntegerField(default=0)
    reading_time = models.PositiveIntegerField(default=1, help_text='Estimated reading time in minutes')

    # SEO
    meta_title = models.CharField(max_length=60, blank=True, verbose_name='SEO Title')
    meta_description = models.CharField(max_length=160, blank=True, verbose_name='SEO Description')

    # Project Details (for Portfolio category)
    project_live_url = models.URLField(max_length=500, blank=True, null=True, verbose_name='Live URL')
    project_price = models.CharField(max_length=100, blank=True, null=True, verbose_name='Project Price', help_text='e.g., "$500", "Starting at $1000", "Fixed"')

    # Timestamps
    published_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Post'
        verbose_name_plural = 'Posts'
        ordering = ['-published_at', '-created_at']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            counter = 1
            while Post.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        # Calculate reading time (avg 200 words/min + 12s per image)
        if self.content:
            from django.utils.html import strip_tags
            plain = strip_tags(self.content)
            word_count = len(plain.split())
            
            img_count = len(re.findall(r'<img[^>]+>', self.content))
            image_time_seconds = img_count * 12
            
            total_minutes = (word_count / 200) + (image_time_seconds / 60)
            self.reading_time = max(1, math.ceil(total_minutes))
        # Auto-generate excerpt from content
        if not self.excerpt and self.content:
            from django.utils.html import strip_tags
            plain = strip_tags(self.content)
            self.excerpt = plain[:300] + '...' if len(plain) > 300 else plain
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('blog:post_detail', kwargs={'slug': self.slug})

    @property
    def seo_title(self):
        return self.meta_title or self.title

    @property
    def seo_description(self):
        return self.meta_description or self.excerpt[:160]

    def increment_views(self):
        self.views_count += 1
        self.save(update_fields=['views_count'])


class Comment(models.Model):
    """Threaded comment system for blog posts."""

    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='comments',
    )
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='replies',
    )
    content = models.TextField(max_length=1000)
    is_approved = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'Comment by {self.author.username} on {self.post.title}'

    @property
    def is_reply(self):
        return self.parent is not None


class PostLike(models.Model):
    """Like/bookmark system for posts."""

    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='likes')
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='liked_posts',
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['post', 'user']

    def __str__(self):
        return f'{self.user.username} likes {self.post.title}'

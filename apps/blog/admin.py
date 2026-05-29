from django.contrib import admin
from .models import Post, Category, Tag, Comment, PostLike


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'post_count', 'order', 'created_at']
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ['order']
    search_fields = ['name']


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name']


class CommentInline(admin.TabularInline):
    model = Comment
    extra = 0
    readonly_fields = ['author', 'content', 'created_at']
    fields = ['author', 'content', 'is_approved', 'created_at']


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'category', 'status', 'is_featured', 'is_premium', 'views_count', 'published_at']
    list_filter = ['status', 'is_featured', 'is_premium', 'category', 'created_at']
    search_fields = ['title', 'content', 'excerpt']
    prepopulated_fields = {'slug': ('title',)}
    list_editable = ['status', 'is_featured', 'is_premium']
    date_hierarchy = 'created_at'
    inlines = [CommentInline]
    filter_horizontal = ['tags']
    readonly_fields = ['views_count', 'reading_time']

    fieldsets = (
        ('Content', {
            'fields': ('title', 'slug', 'content', 'excerpt', 'featured_image'),
        }),
        ('Organization', {
            'fields': ('author', 'category', 'tags'),
        }),
        ('Publishing', {
            'fields': ('status', 'is_premium', 'is_featured', 'published_at'),
        }),
        ('SEO', {
            'fields': ('meta_title', 'meta_description'),
            'classes': ('collapse',),
        }),
        ('Metrics', {
            'fields': ('views_count', 'reading_time'),
            'classes': ('collapse',),
        }),
    )

    actions = ['make_published', 'make_draft', 'make_featured']

    @admin.action(description='Publish selected posts')
    def make_published(self, request, queryset):
        from django.utils import timezone
        queryset.update(status='published', published_at=timezone.now())

    @admin.action(description='Set selected posts as draft')
    def make_draft(self, request, queryset):
        queryset.update(status='draft')

    @admin.action(description='Feature selected posts')
    def make_featured(self, request, queryset):
        queryset.update(is_featured=True)


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['author', 'post', 'is_approved', 'created_at']
    list_filter = ['is_approved', 'created_at']
    search_fields = ['content', 'author__username']
    list_editable = ['is_approved']
    actions = ['approve_comments']

    @admin.action(description='Approve selected comments')
    def approve_comments(self, request, queryset):
        queryset.update(is_approved=True)

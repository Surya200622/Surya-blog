from django.contrib import admin
from .models import Project, Bid, Milestone, Review, ProjectCategory


@admin.register(ProjectCategory)
class ProjectCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ['title', 'client', 'assigned_to', 'budget_display', 'status', 'bid_count', 'created_at']
    list_filter = ['status', 'budget_type', 'category']
    search_fields = ['title', 'description']
    prepopulated_fields = {'slug': ('title',)}


@admin.register(Bid)
class BidAdmin(admin.ModelAdmin):
    list_display = ['freelancer', 'project', 'amount', 'delivery_days', 'status', 'created_at']
    list_filter = ['status']
    search_fields = ['freelancer__username', 'project__title']


@admin.register(Milestone)
class MilestoneAdmin(admin.ModelAdmin):
    list_display = ['title', 'project', 'amount', 'status', 'due_date']
    list_filter = ['status']


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['reviewer', 'reviewee', 'project', 'rating', 'created_at']
    list_filter = ['rating']

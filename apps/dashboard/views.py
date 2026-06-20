from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.decorators import method_decorator
from django.views import View
from django.db.models import Sum, Count, Avg
from django.db.models.functions import TruncMonth
from django.utils import timezone
from datetime import timedelta

from apps.blog.models import Post, Comment, PostLike
from apps.payments.models import Payment, Order
from apps.freelance.models import Project, Bid


@method_decorator(login_required, name='dispatch')
class DashboardHomeView(View):
    """Main dashboard with overview stats."""

    def get(self, request):
        user = request.user
        if not user.is_superuser:
            return redirect('dashboard:settings')

        # Blog stats
        user_posts = Post.objects.filter(author=user)
        total_posts = user_posts.count()
        published_posts = user_posts.filter(status='published').count()
        total_views = user_posts.aggregate(views=Sum('views_count'))['views'] or 0
        total_comments = Comment.objects.filter(post__author=user).count()
        total_likes = PostLike.objects.filter(post__author=user).count()

        # Recent posts
        recent_posts = user_posts.order_by('-created_at')[:5]

        # Recent comments on user's posts
        recent_comments = Comment.objects.filter(
            post__author=user
        ).select_related('author', 'post').order_by('-created_at')[:5]

        # Payment stats
        total_earnings = Payment.objects.filter(
            order__user=user, status='captured'
        ).aggregate(total=Sum('amount'))['total'] or 0

        # Freelance stats
        active_projects = Project.objects.filter(
            client=user, status='in_progress'
        ).count()

        context = {
            'total_posts': total_posts,
            'published_posts': published_posts,
            'total_views': total_views,
            'total_comments': total_comments,
            'total_likes': total_likes,
            'total_earnings': total_earnings,
            'active_projects': active_projects,
            'recent_posts': recent_posts,
            'recent_comments': recent_comments,
            'page_title': 'Dashboard',
        }
        return render(request, 'dashboard/index.html', context)


@method_decorator(login_required, name='dispatch')
class DashboardPostsView(View):
    """Manage user's blog posts."""

    def get(self, request):
        if not request.user.is_superuser:
            return redirect('dashboard:settings')
            
        status_filter = request.GET.get('status', 'all')
        posts = Post.objects.filter(author=request.user)

        if status_filter != 'all':
            posts = posts.filter(status=status_filter)

        context = {
            'posts': posts.order_by('-created_at'),
            'status_filter': status_filter,
            'page_title': 'My Posts',
        }
        return render(request, 'dashboard/posts.html', context)


@method_decorator(login_required, name='dispatch')
class DashboardAnalyticsView(View):
    """Analytics and charts."""

    def get(self, request):
        user = request.user
        if not user.is_superuser:
            return redirect('dashboard:settings')
            
        posts = Post.objects.filter(author=user, status='published')

        # Top posts by views
        top_posts = posts.order_by('-views_count')[:10]

        # Monthly post count (last 6 months)
        six_months_ago = timezone.now() - timedelta(days=180)
        monthly_posts = posts.filter(
            published_at__gte=six_months_ago
        ).annotate(
            month=TruncMonth('published_at')
        ).values('month').annotate(
            count=Count('id'),
            views=Sum('views_count'),
        ).order_by('month')

        context = {
            'top_posts': top_posts,
            'monthly_posts': list(monthly_posts),
            'page_title': 'Analytics',
        }
        return render(request, 'dashboard/analytics.html', context)


@method_decorator(login_required, name='dispatch')
class DashboardPaymentsView(View):
    """Payment history and earnings."""

    def get(self, request):
        if not request.user.is_superuser:
            return redirect('dashboard:settings')
            
        payments = Payment.objects.filter(
            order__user=request.user
        ).select_related('order').order_by('-created_at')

        total_earned = payments.filter(status='captured').aggregate(
            total=Sum('amount')
        )['total'] or 0

        context = {
            'payments': payments,
            'total_earned': total_earned,
            'page_title': 'Payment History',
        }
        return render(request, 'dashboard/payments.html', context)


@method_decorator(login_required, name='dispatch')
class DashboardSettingsView(View):
    """Account settings."""

    def get(self, request):
        from apps.accounts.forms import UserUpdateForm, ProfileUpdateForm
        from apps.accounts.models import Profile

        profile, _ = Profile.objects.get_or_create(user=request.user)

        context = {
            'user_form': UserUpdateForm(instance=request.user),
            'profile_form': ProfileUpdateForm(instance=profile),
            'page_title': 'Settings',
        }
        return render(request, 'dashboard/settings.html', context)

    def post(self, request):
        from apps.accounts.forms import UserUpdateForm, ProfileUpdateForm
        from apps.accounts.models import Profile

        profile, _ = Profile.objects.get_or_create(user=request.user)
        user_form = UserUpdateForm(request.POST, request.FILES, instance=request.user)
        profile_form = ProfileUpdateForm(request.POST, instance=profile)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Settings updated! ✅')
            return redirect('dashboard:settings')

        context = {
            'user_form': user_form,
            'profile_form': profile_form,
            'page_title': 'Settings',
        }
        return render(request, 'dashboard/settings.html', context)


@method_decorator(login_required, name='dispatch')
class DashboardSavedItemsView(View):
    """View saved/liked posts."""

    def get(self, request):
        saved_posts = PostLike.objects.filter(user=request.user).select_related('post__category', 'post__author').order_by('-created_at')

        context = {
            'saved_posts': saved_posts,
            'page_title': 'Saved Items',
        }
        return render(request, 'dashboard/saved.html', context)

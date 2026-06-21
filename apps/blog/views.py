from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views import View
from django.utils.decorators import method_decorator
from django.utils import timezone
from django.db.models import Q
from django.http import JsonResponse
from django.core.paginator import Paginator

from .models import Post, Category, Tag, Comment, PostLike
from .forms import PostForm, ProjectForm, CommentForm, SearchForm


class PostListView(View):
    """Display paginated list of published blog posts."""

    def get(self, request):
        from django.db.models import Q
        posts = Post.objects.filter(Q(project_live_url__isnull=True) | Q(project_live_url=''), status='published').select_related('author', 'category')
        featured_posts = posts.filter(is_featured=True)[:3]
        categories = Category.objects.all()
        tags = Tag.objects.all()

        # Pagination
        paginator = Paginator(posts, 9)
        page = request.GET.get('page', 1)
        posts_page = paginator.get_page(page)

        context = {
            'posts': posts_page,
            'featured_posts': featured_posts,
            'categories': categories,
            'tags': tags,
            'page_title': 'Blog',
            'meta_description': 'Explore our latest articles on technology, development, and design.',
        }
        if request.headers.get('HX-Request') == 'true':
            return render(request, 'blog/partials/post_list_items.html', context)
        return render(request, 'blog/post_list.html', context)


class ProjectListView(View):
    """Display paginated list of portfolio projects."""

    def get(self, request):
        from django.db.models import Q
        posts = Post.objects.exclude(Q(project_live_url__isnull=True) | Q(project_live_url='')).filter(status='published').select_related('author', 'category')
        categories = Category.objects.all()

        paginator = Paginator(posts, 9)
        page = request.GET.get('page', 1)
        posts_page = paginator.get_page(page)

        trending_projects = Post.objects.exclude(Q(project_live_url__isnull=True) | Q(project_live_url='')).filter(status='published').order_by('-views_count')[:3]

        context = {
            'posts': posts_page,
            'categories': categories,
            'trending_projects': trending_projects,
            'page_title': 'Portfolio Projects',
            'meta_description': 'Explore our latest portfolio projects.',
        }
        if request.headers.get('HX-Request') == 'true':
            return render(request, 'blog/partials/post_list_items.html', context)
        return render(request, 'blog/project_list.html', context)
class PostDetailView(View):
    """Display a single blog post with comments."""

    def get(self, request, slug):
        queryset = Post.objects.select_related('author', 'category')
        post_obj = queryset.filter(slug=slug).first()
        if not (request.user.is_authenticated and post_obj and (request.user.is_superuser or request.user == post_obj.author)):
            queryset = queryset.filter(status='published')
        
        post = get_object_or_404(queryset, slug=slug)

        # Increment view count
        post.increment_views()

        # Comments
        comments = post.comments.filter(
            is_approved=True, parent=None
        ).select_related('author').prefetch_related('replies__author')

        # Related posts (Smart matching by Tags)
        from django.db.models import Count
        related_posts = Post.objects.filter(
            status='published',
            tags__in=post.tags.all()
        ).exclude(id=post.id).annotate(
            common_tags=Count('tags')
        ).order_by('-common_tags')[:3]

        if not related_posts:
            related_posts = Post.objects.filter(
                status='published',
                category=post.category,
            ).exclude(id=post.id)[:3]

        # Check if user liked the post
        is_liked = False
        if request.user.is_authenticated:
            is_liked = PostLike.objects.filter(post=post, user=request.user).exists()

        context = {
            'post': post,
            'comments': comments,
            'comment_form': CommentForm(),
            'related_posts': related_posts,
            'is_liked': is_liked,
            'likes_count': post.likes.count(),
            'page_title': post.seo_title,
            'meta_description': post.seo_description,
        }
        return render(request, 'blog/post_detail.html', context)


@method_decorator(login_required, name='dispatch')
class PostCreateView(View):
    """Create a new blog post."""

    def get(self, request):
        if not request.user.is_superuser:
            messages.error(request, 'Only the admin can create posts and projects.')
            return redirect('blog:post_list')
        form = PostForm()
        return render(request, 'blog/post_create.html', {
            'form': form,
            'page_title': 'Create Post',
        })

    def post(self, request):
        if not request.user.is_superuser:
            messages.error(request, 'Only the admin can create posts and projects.')
            return redirect('blog:post_list')

        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            if post.status == 'published' and not post.published_at:
                post.published_at = timezone.now()
            post.save()
            form.save_m2m()
            # Handle tags and category via form
            form.save(commit=True)
            messages.success(request, 'Post created successfully! 📝')
            return redirect('blog:post_detail', slug=post.slug)
        return render(request, 'blog/post_create.html', {'form': form, 'page_title': 'Create Post'})


@method_decorator(login_required, name='dispatch')
class ProjectCreateView(View):
    """Create a new portfolio project."""

    def get(self, request):
        if not request.user.is_superuser:
            messages.error(request, 'Only the admin can create posts and projects.')
            return redirect('blog:project_list')
        form = ProjectForm()
        return render(request, 'blog/project_create.html', {
            'form': form,
            'page_title': 'Create Project',
        })

    def post(self, request):
        if not request.user.is_superuser:
            messages.error(request, 'Only the admin can create posts and projects.')
            return redirect('blog:project_list')

        form = ProjectForm(request.POST, request.FILES)
        if form.is_valid():
            project = form.save(commit=False)
            project.author = request.user
            if project.status == 'published' and not project.published_at:
                project.published_at = timezone.now()
            project.save()
            form.save_m2m()
            # Handle tags and category via form
            form.save(commit=True)
            messages.success(request, 'Project created successfully! 💼')
            return redirect('blog:post_detail', slug=project.slug)
        return render(request, 'blog/project_create.html', {'form': form, 'page_title': 'Create Project'})


@method_decorator(login_required, name='dispatch')
class PostUpdateView(View):
    """Edit an existing blog post."""

    def get(self, request, slug):
        if not request.user.is_superuser:
            messages.error(request, 'Permission denied.')
            return redirect('blog:post_list')
        post = get_object_or_404(Post, slug=slug, author=request.user)
        form = PostForm(instance=post)
        # Pre-fill tags
        form.fields['tags_input'].initial = ', '.join(post.tags.values_list('name', flat=True))
        return render(request, 'blog/post_create.html', {
            'form': form,
            'post': post,
            'is_edit': True,
            'page_title': f'Edit: {post.title}',
        })

    def post(self, request, slug):
        if not request.user.is_superuser:
            messages.error(request, 'Permission denied.')
            return redirect('blog:post_list')
        post = get_object_or_404(Post, slug=slug, author=request.user)
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            post = form.save(commit=False)
            if post.status == 'published' and not post.published_at:
                post.published_at = timezone.now()
            post.save()
            form.save_m2m()
            # Handle tags and category via form
            form.save(commit=True)
            messages.success(request, 'Post updated successfully!')
            return redirect('blog:post_detail', slug=post.slug)
        return render(request, 'blog/post_create.html', {
            'form': form,
            'post': post,
            'is_edit': True,
            'page_title': f'Edit: {post.title}',
        })


@method_decorator(login_required, name='dispatch')
class ProjectUpdateView(View):
    """Edit an existing portfolio project."""

    def get(self, request, slug):
        if not request.user.is_superuser:
            messages.error(request, 'Permission denied.')
            return redirect('blog:project_list')
        project = get_object_or_404(Post, slug=slug, author=request.user)
        form = ProjectForm(instance=project)
        # Pre-fill tags
        form.fields['tags_input'].initial = ', '.join(project.tags.values_list('name', flat=True))
        return render(request, 'blog/project_create.html', {
            'form': form,
            'post': project,
            'is_edit': True,
            'page_title': f'Edit: {project.title}',
        })

    def post(self, request, slug):
        if not request.user.is_superuser:
            messages.error(request, 'Permission denied.')
            return redirect('blog:project_list')
        project = get_object_or_404(Post, slug=slug, author=request.user)
        form = ProjectForm(request.POST, request.FILES, instance=project)
        if form.is_valid():
            project = form.save(commit=False)
            if project.status == 'published' and not project.published_at:
                project.published_at = timezone.now()
            project.save()
            form.save_m2m()
            # Handle tags and category via form
            form.save(commit=True)
            messages.success(request, 'Project updated successfully!')
            return redirect('blog:post_detail', slug=project.slug)
        return render(request, 'blog/project_create.html', {
            'form': form,
            'post': project,
            'is_edit': True,
            'page_title': f'Edit: {project.title}',
        })


@method_decorator(login_required, name='dispatch')
class PostDeleteView(View):
    """Delete a blog post."""

    def post(self, request, slug):
        if not request.user.is_superuser:
            messages.error(request, 'Permission denied.')
            return redirect('dashboard:posts')
        post = get_object_or_404(Post, slug=slug, author=request.user)
        post.delete()
        messages.success(request, 'Post deleted.')
        return redirect('dashboard:posts')


class CategoryView(View):
    """Display posts in a specific category."""

    def get(self, request, slug):
        category = get_object_or_404(Category, slug=slug)
        posts = Post.objects.filter(
            status='published',
            category=category,
        ).select_related('author')

        paginator = Paginator(posts, 9)
        page = request.GET.get('page', 1)
        posts_page = paginator.get_page(page)

        context = {
            'category': category,
            'posts': posts_page,
            'page_title': f'{category.name} Articles',
            'meta_description': category.description or f'Browse {category.name} articles.',
        }
        return render(request, 'blog/category_list.html', context)


class TagView(View):
    """Display posts with a specific tag."""

    def get(self, request, slug):
        tag = get_object_or_404(Tag, slug=slug)
        posts = Post.objects.filter(
            status='published',
            tags=tag,
        ).select_related('author', 'category')

        paginator = Paginator(posts, 9)
        page = request.GET.get('page', 1)
        posts_page = paginator.get_page(page)

        context = {
            'tag': tag,
            'posts': posts_page,
            'page_title': f'Posts tagged: {tag.name}',
        }
        return render(request, 'blog/post_list.html', context)


class SearchView(View):
    """Search blog posts."""

    def get(self, request):
        query = request.GET.get('q', '')
        posts = Post.objects.none()

        if query:
            posts = Post.objects.filter(
                Q(title__icontains=query) |
                Q(content__icontains=query) |
                Q(excerpt__icontains=query) |
                Q(tags__name__icontains=query),
                Q(tags__name__icontains=query),
                status='published',
            ).distinct().select_related('author', 'category')

        if request.headers.get('HX-Request'):
            return render(request, 'blog/partials/search_results.html', {'posts': posts[:5]})

        paginator = Paginator(posts, 9)
        page = request.GET.get('page', 1)
        posts_page = paginator.get_page(page)

        context = {
            'posts': posts_page,
            'query': query,
            'results_count': posts.count(),
            'search_form': SearchForm(initial={'q': query}),
            'page_title': f'Search: {query}' if query else 'Search',
        }
        return render(request, 'blog/search_results.html', context)


@login_required
def add_comment(request, slug):
    """Add a comment to a post (HTMX endpoint)."""
    post = get_object_or_404(Post, slug=slug, status='published')

    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.author = request.user

            # Check for parent comment (replies)
            parent_id = request.POST.get('parent_id')
            if parent_id:
                comment.parent = get_object_or_404(Comment, id=parent_id)

            comment.save()

            if request.headers.get('HX-Request'):
                comments = post.comments.filter(
                    is_approved=True, parent=None
                ).select_related('author').prefetch_related('replies__author')
                return render(request, 'blog/partials/comments_list.html', {
                    'comments': comments,
                    'post': post,
                })

            messages.success(request, 'Comment added!')
            return redirect('blog:post_detail', slug=slug)

    return redirect('blog:post_detail', slug=slug)


@login_required
def toggle_like(request, slug):
    """Toggle like on a post (AJAX endpoint)."""
    post = get_object_or_404(Post, slug=slug, status='published')

    like, created = PostLike.objects.get_or_create(post=post, user=request.user)
    if not created:
        like.delete()
        liked = False
    else:
        liked = True

    return JsonResponse({
        'liked': liked,
        'count': post.likes.count(),
    })

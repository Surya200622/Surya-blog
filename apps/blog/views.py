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
from .forms import PostForm, CommentForm, SearchForm


class PostListView(View):
    """Display paginated list of published blog posts."""

    def get(self, request):
        posts = Post.objects.filter(status='published').select_related('author', 'category')
        featured_posts = posts.filter(is_featured=True)[:3]
        categories = Category.objects.all()

        # Pagination
        paginator = Paginator(posts, 9)
        page = request.GET.get('page', 1)
        posts_page = paginator.get_page(page)

        context = {
            'posts': posts_page,
            'featured_posts': featured_posts,
            'categories': categories,
            'page_title': 'Blog',
            'meta_description': 'Explore our latest articles on technology, development, and design.',
        }
        return render(request, 'blog/post_list.html', context)


class PostDetailView(View):
    """Display a single blog post with comments."""

    def get(self, request, slug):
        post = get_object_or_404(
            Post.objects.select_related('author', 'category'),
            slug=slug,
            status='published',
        )

        # Increment view count
        post.increment_views()

        # Comments
        comments = post.comments.filter(
            is_approved=True, parent=None
        ).select_related('author').prefetch_related('replies__author')

        # Related posts
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
        return render(request, 'blog/post_create.html', {'form': form})


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
                status='published',
            ).distinct().select_related('author', 'category')

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

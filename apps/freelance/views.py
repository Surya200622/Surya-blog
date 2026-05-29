from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.decorators import method_decorator
from django.views import View
from django.core.paginator import Paginator
from django.db.models import Q, Avg

from .models import Project, Bid, Milestone, Review, ProjectCategory
from .forms import ProjectForm, BidForm, ReviewForm, MilestoneForm


class ProjectListView(View):
    """Browse open freelance projects."""

    def get(self, request):
        projects = Project.objects.filter(status='open').select_related('client', 'category')

        # Filters
        category_slug = request.GET.get('category')
        budget_min = request.GET.get('budget_min')
        budget_max = request.GET.get('budget_max')
        query = request.GET.get('q', '')

        if category_slug:
            projects = projects.filter(category__slug=category_slug)
        if budget_min:
            projects = projects.filter(budget_max__gte=budget_min)
        if budget_max:
            projects = projects.filter(budget_min__lte=budget_max)
        if query:
            projects = projects.filter(
                Q(title__icontains=query) | Q(description__icontains=query)
            )

        categories = ProjectCategory.objects.all()

        paginator = Paginator(projects, 12)
        page = request.GET.get('page', 1)
        projects_page = paginator.get_page(page)

        context = {
            'projects': projects_page,
            'categories': categories,
            'query': query,
            'page_title': 'Find Projects',
            'meta_description': 'Browse open freelance projects and start earning.',
        }
        return render(request, 'freelance/project_list.html', context)


class ProjectDetailView(View):
    """View project details and submit bids."""

    def get(self, request, slug):
        project = get_object_or_404(
            Project.objects.select_related('client', 'category', 'assigned_to'),
            slug=slug,
        )
        bids = project.bids.select_related('freelancer')

        # Only show bid form if user is a freelancer and hasn't bid yet
        can_bid = False
        user_bid = None
        if request.user.is_authenticated:
            user_bid = project.bids.filter(freelancer=request.user).first()
            can_bid = (
                request.user.is_freelancer and
                project.status == 'open' and
                user_bid is None and
                project.client != request.user
            )

        milestones = project.milestones.all()
        reviews = project.reviews.select_related('reviewer', 'reviewee')

        context = {
            'project': project,
            'bids': bids if request.user == project.client else bids[:0],
            'bid_count': bids.count(),
            'can_bid': can_bid,
            'user_bid': user_bid,
            'bid_form': BidForm() if can_bid else None,
            'milestones': milestones,
            'reviews': reviews,
            'page_title': project.title,
        }
        return render(request, 'freelance/project_detail.html', context)


@method_decorator(login_required, name='dispatch')
class ProjectCreateView(View):
    """Create a new freelance project."""

    def get(self, request):
        if not request.user.is_superuser:
            messages.error(request, 'Only the admin can post projects.')
            return redirect('freelance:project_list')
        form = ProjectForm()
        return render(request, 'freelance/project_create.html', {
            'form': form,
            'page_title': 'Post a Project',
        })

    def post(self, request):
        if not request.user.is_superuser:
            messages.error(request, 'Only the admin can post projects.')
            return redirect('freelance:project_list')
        form = ProjectForm(request.POST, request.FILES)
        if form.is_valid():
            project = form.save(commit=False)
            project.client = request.user
            project.save()
            messages.success(request, 'Project posted successfully! 🚀')
            return redirect('freelance:project_detail', slug=project.slug)
        return render(request, 'freelance/project_create.html', {'form': form})


@method_decorator(login_required, name='dispatch')
class SubmitBidView(View):
    """Submit a bid on a project."""

    def post(self, request, slug):
        project = get_object_or_404(Project, slug=slug, status='open')

        if project.client == request.user:
            messages.error(request, "You can't bid on your own project.")
            return redirect('freelance:project_detail', slug=slug)

        if Bid.objects.filter(project=project, freelancer=request.user).exists():
            messages.error(request, "You've already submitted a bid.")
            return redirect('freelance:project_detail', slug=slug)

        form = BidForm(request.POST)
        if form.is_valid():
            bid = form.save(commit=False)
            bid.project = project
            bid.freelancer = request.user
            bid.save()
            messages.success(request, 'Bid submitted successfully!')
            return redirect('freelance:project_detail', slug=slug)

        messages.error(request, 'Please fix the errors below.')
        return redirect('freelance:project_detail', slug=slug)


@method_decorator(login_required, name='dispatch')
class AcceptBidView(View):
    """Client accepts a bid and assigns the freelancer."""

    def post(self, request, bid_id):
        bid = get_object_or_404(Bid, id=bid_id, project__client=request.user)
        project = bid.project

        # Accept this bid, reject others
        bid.status = 'accepted'
        bid.save()

        project.bids.exclude(id=bid.id).update(status='rejected')
        project.assigned_to = bid.freelancer
        project.status = 'in_progress'
        project.save()

        messages.success(request, f'Bid accepted! {bid.freelancer.username} has been assigned.')
        return redirect('freelance:project_detail', slug=project.slug)


@method_decorator(login_required, name='dispatch')
class MyProjectsView(View):
    """View user's projects (as client or freelancer)."""

    def get(self, request):
        role = request.GET.get('role', 'client')

        if role == 'freelancer':
            projects = Project.objects.filter(assigned_to=request.user)
            bids = Bid.objects.filter(freelancer=request.user).select_related('project')
        else:
            projects = Project.objects.filter(client=request.user)
            bids = None

        context = {
            'projects': projects,
            'bids': bids,
            'role': role,
            'page_title': 'My Projects',
        }
        return render(request, 'freelance/my_projects.html', context)


@method_decorator(login_required, name='dispatch')
class CreateReviewView(View):
    """Leave a review after project completion."""

    def post(self, request, slug):
        project = get_object_or_404(Project, slug=slug, status='completed')

        # Determine reviewee
        if request.user == project.client:
            reviewee = project.assigned_to
        elif request.user == project.assigned_to:
            reviewee = project.client
        else:
            messages.error(request, 'You cannot review this project.')
            return redirect('freelance:project_detail', slug=slug)

        if Review.objects.filter(project=project, reviewer=request.user).exists():
            messages.error(request, "You've already reviewed this project.")
            return redirect('freelance:project_detail', slug=slug)

        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.project = project
            review.reviewer = request.user
            review.reviewee = reviewee
            review.save()

            # Update reviewee's profile rating
            avg_rating = Review.objects.filter(reviewee=reviewee).aggregate(
                avg=Avg('rating')
            )['avg'] or 0
            profile = reviewee.profile
            profile.rating = round(avg_rating, 1)
            profile.total_reviews = Review.objects.filter(reviewee=reviewee).count()
            profile.save()

            messages.success(request, 'Review submitted! ⭐')
            return redirect('freelance:project_detail', slug=slug)

        messages.error(request, 'Please fix the errors.')
        return redirect('freelance:project_detail', slug=slug)

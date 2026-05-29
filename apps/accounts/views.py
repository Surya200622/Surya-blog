from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views import View
from django.utils.decorators import method_decorator

from .forms import CustomRegistrationForm, CustomLoginForm, UserUpdateForm, ProfileUpdateForm
from .models import CustomUser, Profile


class RegisterView(View):
    """User registration view."""

    def get(self, request):
        if request.user.is_authenticated:
            return redirect('dashboard:home')
        form = CustomRegistrationForm()
        return render(request, 'accounts/register.html', {'form': form})

    def post(self, request):
        form = CustomRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            messages.success(request, f'Welcome to BlogCraft, {user.username}! 🎉')
            return redirect('dashboard:home')
        return render(request, 'accounts/register.html', {'form': form})


class LoginView(View):
    """User login view."""

    def get(self, request):
        if request.user.is_authenticated:
            return redirect('dashboard:home')
        form = CustomLoginForm()
        return render(request, 'accounts/login.html', {'form': form})

    def post(self, request):
        form = CustomLoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            messages.success(request, f'Welcome back, {user.username}!')
            next_url = request.GET.get('next', 'dashboard:home')
            return redirect(next_url)
        return render(request, 'accounts/login.html', {'form': form})


class LogoutView(View):
    """User logout view."""

    def post(self, request):
        logout(request)
        messages.info(request, 'You have been logged out.')
        return redirect('pages:home')

    def get(self, request):
        logout(request)
        messages.info(request, 'You have been logged out.')
        return redirect('pages:home')


@method_decorator(login_required, name='dispatch')
class ProfileView(View):
    """View and edit user profile."""

    def get(self, request, username=None):
        if username:
            user = get_object_or_404(CustomUser, username=username)
            is_own = request.user == user
        else:
            user = request.user
            is_own = True

        profile, _ = Profile.objects.get_or_create(user=user)

        context = {
            'profile_user': user,
            'profile': profile,
            'is_own_profile': is_own,
        }

        if is_own:
            context['user_form'] = UserUpdateForm(instance=user)
            context['profile_form'] = ProfileUpdateForm(instance=profile)

        return render(request, 'accounts/profile.html', context)

    def post(self, request, username=None):
        user = request.user
        profile, _ = Profile.objects.get_or_create(user=user)

        user_form = UserUpdateForm(request.POST, request.FILES, instance=user)
        profile_form = ProfileUpdateForm(request.POST, instance=profile)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('accounts:profile_view', username=user.username)

        context = {
            'profile_user': user,
            'profile': profile,
            'is_own_profile': True,
            'user_form': user_form,
            'profile_form': profile_form,
        }
        return render(request, 'accounts/profile.html', context)


class PublicProfileView(View):
    """Public profile page for any user."""

    def get(self, request, username):
        user = get_object_or_404(CustomUser, username=username)
        profile, _ = Profile.objects.get_or_create(user=user)

        # Get user's published posts
        posts = user.blog_posts.filter(status='published').order_by('-published_at')[:6]

        context = {
            'profile_user': user,
            'profile': profile,
            'is_own_profile': request.user == user if request.user.is_authenticated else False,
            'recent_posts': posts,
        }
        return render(request, 'accounts/public_profile.html', context)

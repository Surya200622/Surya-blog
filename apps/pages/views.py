from django.shortcuts import render, redirect
from django.contrib import messages
from django.views import View
from django.core.mail import send_mail
from django.conf import settings

from apps.blog.models import Post, Category
from apps.payments.models import Plan
from .forms import ContactForm


class HomeView(View):
    """Landing page."""

    def get(self, request):
        featured_posts = Post.objects.filter(
            status='published', is_featured=True
        ).select_related('author', 'category')[:3]

        latest_posts = Post.objects.filter(
            status='published'
        ).exclude(category__slug='portfolio').order_by('-published_at')[:3]

        portfolio_posts = Post.objects.filter(
            status='published', category__slug='portfolio'
        ).order_by('-published_at')[:4]

        plans = Plan.objects.filter(is_active=True).order_by('price')[:3]

        categories = Category.objects.all()[:4]

        context = {
            'featured_posts': featured_posts,
            'latest_posts': latest_posts,
            'portfolio_posts': portfolio_posts,
            'plans': plans,
            'categories': categories,
            'page_title': 'Home',
            'meta_description': 'BlogCraft — A premium blog and freelance platform. Read, write, and hire top talent.',
        }
        return render(request, 'pages/home.html', context)


class AboutView(View):
    """About page."""

    def get(self, request):
        context = {
            'page_title': 'About Us',
            'meta_description': 'Learn about BlogCraft — our mission, team, and vision for the future of freelancing.',
        }
        return render(request, 'pages/about.html', context)


class ContactView(View):
    """Contact page with form."""

    def get(self, request):
        form = ContactForm()
        context = {
            'form': form,
            'page_title': 'Contact Us',
            'meta_description': 'Get in touch with the BlogCraft team. We\'d love to hear from you.',
        }
        return render(request, 'pages/contact.html', context)

    def post(self, request):
        form = ContactForm(request.POST)
        if form.is_valid():
            # Send email
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            subject = form.cleaned_data['subject']
            message = form.cleaned_data['message']

            try:
                send_mail(
                    subject=f'[BlogCraft Contact] {subject}',
                    message=f'From: {name} ({email})\n\n{message}',
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[settings.DEFAULT_FROM_EMAIL],
                    fail_silently=True,
                )
            except Exception:
                pass

            messages.success(request, 'Message sent! We\'ll get back to you soon. ✉️')
            return redirect('pages:contact')

        context = {
            'form': form,
            'page_title': 'Contact Us',
        }
        return render(request, 'pages/contact.html', context)

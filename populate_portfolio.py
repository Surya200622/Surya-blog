import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.dev')
django.setup()

from django.contrib.auth import get_user_model
from apps.blog.models import Post, Category, Tag
from apps.payments.models import Plan
from django.utils import timezone

User = get_user_model()

def populate():
    # 1. Get or create author (Surya)
    author, _ = User.objects.get_or_create(username='admin')
    if not author.email:
        author.email = 'cssurya2006@gmail.com'
    author.first_name = 'Surya'
    author.last_name = 'CS'
    author.save()

    # 2. Create Portfolio Category
    portfolio_cat, _ = Category.objects.get_or_create(
        name='Portfolio',
        slug='portfolio',
        defaults={'description': 'Selected projects and digital solutions.', 'icon': 'briefcase'}
    )
    
    # Create other blog categories
    Category.objects.get_or_create(name='Django', slug='django', defaults={'icon': 'code'})
    Category.objects.get_or_create(name='React', slug='react', defaults={'icon': 'atom'})

    # 3. Create Tags
    tags = {}
    for tag_name in ['Python', 'Django', 'HTML/CSS', 'SQLite', 'Bootstrap', 'JavaScript', 'PostgreSQL', 'React.js', 'Vite', 'Framer Motion', 'AI']:
        tags[tag_name], _ = Tag.objects.get_or_create(name=tag_name, slug=tag_name.lower().replace('/', '-').replace(' ', '-').replace('.', '-'))

    # 4. Create Portfolio Posts
    projects = [
        {
            'title': 'DentalExperts',
            'slug': 'dental-experts',
            'excerpt': 'A comprehensive full-stack web application designed to streamline dental appointment booking, clinic information access, and efficient management of patient records & doctor schedules.',
            'content': '<p>A comprehensive full-stack web application designed to streamline dental appointment booking, clinic information access, and efficient management of patient records & doctor schedules.</p>',
            'tags': ['Python', 'Django', 'HTML/CSS', 'SQLite', 'Bootstrap']
        },
        {
            'title': 'CipherApparel',
            'slug': 'cipherapparel',
            'excerpt': 'A responsive fashion e-commerce web application with login/signup, product listings, offers, and dynamic backend integration using Python and web technologies.',
            'content': '<p>A responsive fashion e-commerce web application with login/signup, product listings, offers, and dynamic backend integration using Python and web technologies.</p>',
            'tags': ['Python', 'Django', 'JavaScript', 'Bootstrap', 'PostgreSQL']
        },
        {
            'title': 'Personal Portfolio',
            'slug': 'personal-portfolio',
            'excerpt': 'A responsive portfolio built with React Vite featuring parallax effects to showcase projects, skills, and professional experience.',
            'content': '<p>A responsive portfolio built with React Vite featuring parallax effects to showcase projects, skills, and professional experience.</p>',
            'tags': ['React.js', 'Vite', 'Framer Motion']
        },
        {
            'title': 'Face Swap Photo & Video Editor',
            'slug': 'face-swap-ai',
            'excerpt': 'Professional face swap tool for photos and videos, built with modern web technologies and AI-powered editing capabilities.',
            'content': '<p>Professional face swap tool for photos and videos, built with modern web technologies and AI-powered editing capabilities.</p>',
            'tags': ['AI', 'Python']
        }
    ]

    for p in projects:
        post, created = Post.objects.get_or_create(
            slug=p['slug'],
            defaults={
                'title': p['title'],
                'excerpt': p['excerpt'],
                'content': p['content'],
                'author': author,
                'category': portfolio_cat,
                'status': 'published',
                'published_at': timezone.now(),
                'reading_time': 2
            }
        )
        for t in p['tags']:
            post.tags.add(tags[t])
        print(f"{'Created' if created else 'Updated'} Project: {post.title}")

    # 5. Create Pricing Plans / Offers
    offers = [
        {
            'name': 'Business Website',
            'slug': 'business-website',
            'description': 'Professional web presence for your business. Perfect for agencies, portfolios, and local businesses.',
            'price': 15000,
            'duration_days': 30,
            'features': ['Responsive Design (Mobile + Desktop)', 'Up to 5 Pages', 'Contact Form Integration', 'Basic SEO Setup', '1 Month Support']
        },
        {
            'name': 'E-commerce Store',
            'slug': 'ecommerce-store',
            'description': 'Full-featured online store with payments, cart, and admin dashboard to manage products.',
            'price': 35000,
            'duration_days': 60,
            'features': ['Payment Gateway Integration', 'Product Management', 'User Authentication', 'Shopping Cart & Orders', '3 Months Support']
        },
        {
            'name': 'Custom SaaS App',
            'slug': 'custom-saas',
            'description': 'Tailored software-as-a-service platform with user roles, subscriptions, and complex logic.',
            'price': 50000,
            'duration_days': 90,
            'features': ['Advanced Backend (Django)', 'Dynamic Frontend (React)', 'Subscription Billing', 'Admin/Client Dashboards', '6 Months Support']
        }
    ]

    for o in offers:
        plan, created = Plan.objects.get_or_create(
            slug=o['slug'],
            defaults={
                'name': o['name'],
                'description': o['description'],
                'price': o['price'],
                'duration_days': o['duration_days'],
                'features': o['features'],
                'is_active': True
            }
        )
        print(f"{'Created' if created else 'Updated'} Plan: {plan.name}")

    # Mark middle plan as popular
    ecommerce = Plan.objects.get(slug='ecommerce-store')
    ecommerce.features.append('Recommended')
    ecommerce.save()

if __name__ == '__main__':
    print("Populating database with Surya CS portfolio and offers...")
    populate()
    print("Done!")

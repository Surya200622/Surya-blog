import os
import django
from django.core.files import File
from pathlib import Path

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.dev')
django.setup()

from django.contrib.auth import get_user_model
from django.utils.text import slugify
from apps.blog.models import Post, Category, Tag

User = get_user_model()
PUBLIC_IMG_DIR = Path(r"C:\Users\Classic\Downloads\Magical portfolio\public\images")

def run():
    print("Getting or creating admin user...")
    admin_email = "cssurya2006@gmail.com"
    try:
        user = User.objects.get(email=admin_email)
        if not user.is_superuser:
            user.is_superuser = True
            user.is_staff = True
            user.save()
            print("Updated user to superuser.")
    except User.DoesNotExist:
        user = User.objects.create_superuser('surya_admin', admin_email, 'admin123')
        print("Created new admin user with password 'admin123'.")
    
    # Ensure portfolio category exists
    cat, _ = Category.objects.get_or_create(
        name="Portfolio",
        defaults={"slug": "portfolio", "description": "My Selected Works"}
    )
    
    projects = [
        {
            "title": "Dental Experts",
            "excerpt": "A modern, responsive website for a dental clinic, built for optimal performance.",
            "content": "<p>A modern, responsive website for a dental clinic, built for optimal performance.</p>",
            "live_url": "https://suryacs.pythonanywhere.com/",
            "price": "Starting at $499",
            "image_filename": "Dental experts.png"
        },
        {
            "title": "CipherApparel",
            "excerpt": "A full-featured eCommerce platform for an apparel brand, featuring a seamless shopping experience.",
            "content": "<p>A full-featured eCommerce platform for an apparel brand, featuring a seamless shopping experience.</p>",
            "live_url": "https://cipherapparel.pythonanywhere.com/",
            "price": "Starting at $999",
            "image_filename": "Cipherapparel.png"
        },
        {
            "title": "Personal Portfolio",
            "excerpt": "A high-performance personal portfolio website hosted on Vercel.",
            "content": "<p>A high-performance personal portfolio website hosted on Vercel.</p>",
            "live_url": "https://surya-cs-portfolio.vercel.app/",
            "price": "Starting at $299",
            "image_filename": "vercel hosted portfolio.png"
        },
        {
            "title": "AI Face Swap App",
            "excerpt": "An innovative AI-powered application that seamlessly swaps faces in images.",
            "content": "<p>An innovative AI-powered application that seamlessly swaps faces in images.</p>",
            "live_url": "",
            "price": "Custom",
            "image_filename": "aifaceswap-1aa5aa8b08ca5a887248501bf6968bf3.jpg"
        }
    ]
    
    for p in projects:
        slug = slugify(p["title"])
        try:
            post = Post.objects.get(slug=slug)
            created = False
        except Post.DoesNotExist:
            post = Post(slug=slug)
            created = True
        
        post.title = p["title"]
        post.author = user
        post.category = cat
        post.status = "published"
        post.excerpt = p["excerpt"]
        post.content = p["content"]
        post.project_live_url = p["live_url"]
        post.project_price = p["price"]
            
        # Add image if it exists
        img_path = PUBLIC_IMG_DIR / p["image_filename"]
        if img_path.exists():
            with img_path.open('rb') as f:
                post.featured_image.save(p["image_filename"], File(f), save=False)
        else:
            print(f"Warning: Image not found {img_path}")
            
        post.save()
        print(f"{'Created' if created else 'Updated'} project: {p['title']}")
        
    print("Done populating projects.")

if __name__ == '__main__':
    run()

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.base')
django.setup()

from django.contrib.sites.models import Site

def update_domain():
    site = Site.objects.get(id=1)
    site.domain = 'blogcraft.pythonanywhere.com'
    site.name = 'BlogCraft'
    site.save()
    print(f"Successfully updated Site ID 1 to {site.domain}")

if __name__ == '__main__':
    update_domain()

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.urls import reverse


class CustomUser(AbstractUser):
    """Extended user model with roles and profile data."""

    class Role(models.TextChoices):
        ADMIN = 'admin', 'Admin'
        AUTHOR = 'author', 'Author'
        CLIENT = 'client', 'Client'
        FREELANCER = 'freelancer', 'Freelancer'

    email = models.EmailField(unique=True, verbose_name='Email Address')
    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.AUTHOR,
        verbose_name='User Role',
    )
    avatar = models.ImageField(
        upload_to='avatars/%Y/%m/',
        blank=True,
        null=True,
        verbose_name='Profile Picture',
    )
    bio = models.TextField(max_length=500, blank=True, verbose_name='Bio')
    phone = models.CharField(max_length=15, blank=True, verbose_name='Phone Number')
    website = models.URLField(blank=True, verbose_name='Website')
    is_verified = models.BooleanField(default=False, verbose_name='Verified Account')
    date_joined = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['-date_joined']

    def __str__(self):
        return self.get_full_name() or self.username

    def get_absolute_url(self):
        return reverse('accounts:profile', kwargs={'username': self.username})

    @property
    def avatar_url(self):
        if self.avatar:
            return self.avatar.url
        return '/static/images/default-avatar.svg'

    @property
    def is_author(self):
        return self.role in [self.Role.AUTHOR, self.Role.ADMIN]

    @property
    def is_freelancer(self):
        return self.role in [self.Role.FREELANCER, self.Role.ADMIN]

    @property
    def is_client_role(self):
        return self.role in [self.Role.CLIENT, self.Role.ADMIN]


class Profile(models.Model):
    """Extended profile for freelance features."""

    user = models.OneToOneField(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='profile',
    )
    headline = models.CharField(max_length=200, blank=True, verbose_name='Professional Headline')
    skills = models.JSONField(default=list, blank=True, verbose_name='Skills')
    hourly_rate = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name='Hourly Rate (₹)',
    )
    portfolio_url = models.URLField(blank=True, verbose_name='Portfolio URL')
    github_url = models.URLField(blank=True, verbose_name='GitHub URL')
    linkedin_url = models.URLField(blank=True, verbose_name='LinkedIn URL')
    twitter_url = models.URLField(blank=True, verbose_name='Twitter/X URL')
    rating = models.FloatField(default=0.0, verbose_name='Average Rating')
    total_reviews = models.IntegerField(default=0, verbose_name='Total Reviews')
    total_earnings = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        verbose_name='Total Earnings (₹)',
    )
    total_projects = models.IntegerField(default=0, verbose_name='Completed Projects')
    is_available = models.BooleanField(default=True, verbose_name='Available for Hire')
    location = models.CharField(max_length=100, blank=True, verbose_name='Location')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Profile'
        verbose_name_plural = 'Profiles'

    def __str__(self):
        return f'{self.user.username} Profile'

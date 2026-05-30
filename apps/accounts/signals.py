from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import CustomUser, Profile


@receiver(post_save, sender=CustomUser)
def create_user_profile(sender, instance, created, **kwargs):
    """Auto-create a Profile when a new user is created."""
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=CustomUser)
def save_user_profile(sender, instance, **kwargs):
    """Auto-save the Profile when user is saved."""
    try:
        instance.profile.save()
    except Profile.DoesNotExist:
        Profile.objects.create(user=instance)

try:
    from allauth.account.signals import user_logged_in
    @receiver(user_logged_in)
    def enforce_client_role(sender, user, request, **kwargs):
        """Ensure any non-superuser logging in is strictly forced to Client role."""
        if not user.is_superuser and user.role != CustomUser.Role.CLIENT:
            user.role = CustomUser.Role.CLIENT
            user.save(update_fields=['role'])
except ImportError:
    pass

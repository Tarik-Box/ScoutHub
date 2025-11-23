from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class Profile(models.Model):
    """
    A user's profile info. Extends the default Django User model.
    Holds extra, you know, personal deets like a bio or a favorite player.
    All these extra fields are kinda optional, so no pressure to fill 'em all out.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(max_length=500, blank=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    preferred_position = models.CharField(max_length=100, blank=True)
    idol_player = models.CharField(max_length=100, blank=True, null=True)
    favorite_talent = models.CharField(max_length=100, blank=True, null=True)
    best_coach = models.CharField(max_length=100, blank=True, null=True)
    favorite_club = models.CharField(max_length=100, blank=True, null=True)


    def __str__(self):
        return f'{self.user.username} Profile'

# Signal to create/update user profile
@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
    instance.profile.save()


"""Management command to create profiles for users that don't have one."""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from accounts.models import Profile


class Command(BaseCommand):
    """Creates profiles for any existing users that are missing one."""

    help = "Creates Profile objects for existing Users who do not have one."

    def handle(self, *args, **options):
        """The main logic for the command."""
        users_without_profile = User.objects.filter(profile__isnull=True)
        count = 0
        for user in users_without_profile:
            Profile.objects.create(user=user)
            self.stdout.write(
                self.style.SUCCESS(f"Created profile for user: {user.username}")
            )
            count += 1
        self.stdout.write(
            self.style.SUCCESS(
                f"Successfully created {count} profiles for existing users."
            )
        )


from django.test import TestCase
from django.contrib.auth import get_user_model
from accounts.models import Profile

User = get_user_model()


class ProfileModelTest(TestCase):
    """Test case for the Profile model."""

    def setUp(self):
        """Set up a user and profile for testing."""
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpassword"
        )
        self.profile = Profile.objects.get(user=self.user)

    def test_profile_str_method(self):
        """Test the __str__ method of the Profile model."""
        self.assertEqual(str(self.profile), f"{self.user.username} Profile")
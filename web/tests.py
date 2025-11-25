from django.test import TestCase
from django.urls import reverse


class WebAppTests(TestCase):
    """
    Test suite for the 'web' application.

    this will check if the main pages load up all good.
    """

    def test_home_page_status_code(self):
        """Tests if the homepage returns a 200 OK status code."""
        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 200)

    def test_about_page_status_code(self):
        """Tests if the about page returns a 200 OK status code."""
        response = self.client.get(reverse("about"))
        self.assertEqual(response.status_code, 200)

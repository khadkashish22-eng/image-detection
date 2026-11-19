from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse


class AccountRegressionTests(TestCase):
    def test_login_page_opens_without_redirect_parameter(self):
        response = self.client.get(reverse("login"))
        self.assertEqual(response.status_code, 200)

    def setUp(self):
        self.user = User.objects.create_user(
            username="reviewer", email="old@example.com", password="TestPassword123!"
        )

    def test_login_rejects_external_redirect(self):
        response = self.client.post(reverse("login"), {
            "username": "reviewer", "password": "TestPassword123!",
            "next": "https://example.com/",
        })
        self.assertRedirects(response, reverse("homepage"))

    def test_login_preserves_local_redirect(self):
        response = self.client.post(reverse("login"), {
            "username": "reviewer", "password": "TestPassword123!",
            "next": reverse("user_details"),
        })
        self.assertRedirects(response, reverse("user_details"))

    def test_email_change_is_saved(self):
        self.client.force_login(self.user)
        self.client.post(reverse("user_details"), {
            "change_email": "1", "email": "new@example.com",
        })
        self.user.refresh_from_db()
        self.assertEqual(self.user.email, "new@example.com")

    def test_short_registration_password_is_rejected(self):
        self.client.post(reverse("register"), {
            "first_name": "Test", "last_name": "User", "username": "newuser",
            "email": "new@example.com", "password": "abc1", "password2": "abc1",
        })
        self.assertFalse(User.objects.filter(username="newuser").exists())

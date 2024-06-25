from django.contrib.auth import get_user_model
from django.test import TestCase


class TestModels(TestCase):
    """Tests for all models"""

    def test_create_user_with_email_success(self):
        """Test creating a user with email successfully"""
        email = "test@example.com"
        password = "testpass123456"
        user = get_user_model().objects.create_user(email=email, password=password)
        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

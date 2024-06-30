from decimal import Decimal

from core import models
from django.contrib.auth import get_user_model
from django.test import TestCase


def create_user():
    """Create a new user and return it"""
    return get_user_model().objects.create_user(
        email="example@example.com", password="password23"
    )


class TestModels(TestCase):
    """Tests for all models"""

    def test_create_user_with_email_success(self):
        """Test creating a user with email successfully"""
        email = "test@example.com"
        password = "testpass123456"
        user = get_user_model().objects.create_user(email=email, password=password)
        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normalized(self):
        """Test email is normalized for new users."""
        sample_emails = [
            ["test1@EXAMPLE.com", "test1@example.com"],
            ["Test2@Example.com", "Test2@example.com"],
            ["TEST3@EXAMPLE.com", "TEST3@example.com"],
            ["test4@example.COM", "test4@example.com"],
        ]
        for email, expected in sample_emails:
            user = get_user_model().objects.create_user(email, "sample123")
            self.assertEqual(user.email, expected)

    def test_create_user_without_email_raises_exception(self):
        """When creating a new user without an email, raise a value error"""
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user("", "passwordy1232")

    def test_create_superuser(self):
        """Test creating a superuser"""
        user = get_user_model().objects.create_superuser(
            email="myEmail@example.com", password="password123"
        )
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

    def test_create_new_recipe(self):
        """Test creating a new recipe successfully"""
        user = get_user_model().objects.create_user(
            name="myName", email="myEmail@example.com", password="myPassword2323"
        )
        recipe = models.Recipe.objects.create(
            user=user,
            title="Recipe Title",
            time_minutes=5,
            price=Decimal("5.32"),
            description="Description of a sample recipe",
        )
        self.assertEqual(str(recipe), recipe.title)

    def test_create_new_tag(self):
        """Test creating a new tag successfully"""
        user = create_user()
        tag = models.Tag.objects.create(user=user, name="name 1")

        self.assertEqual(str(tag), tag.name)

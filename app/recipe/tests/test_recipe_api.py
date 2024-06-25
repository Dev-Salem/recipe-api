from core.models import Recipe
from django.test import TestCase
from decimal import Decimal
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from recipe.serializers import RecipeSerializer

RECIPES_LIST_URL = reverse("recipe:recipe-list")


def create_recipe(user, **params):
    defaults = {
        "title": "Test Recipe Name",
        "description": "Test Recipe Description..",
        "time_minutes": 12,
        "price": Decimal("3.53"),
    }
    defaults.update(params)
    return Recipe.objects.create(user=user, **defaults)


class PublicRecipeAPITests(TestCase):
    """Test unauthenticated api requests"""

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email="user@example.com", password="password2334", name="Test User"
        )
        self.client = APIClient()

    def test_get_recipe_list_unauthorized(self):
        """Test returning an error when request is unauthorized"""
        res = self.client.get(RECIPES_LIST_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateAPITests(TestCase):
    """Test authenticated api requests"""

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email="user@example.com", password="password2334", name="Test User"
        )
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrieve_recipe_list_success(self):
        """Test retrieving recipes successfully"""
        create_recipe(self.user)
        create_recipe(self.user)
        res = self.client.get(RECIPES_LIST_URL)
        recipes = Recipe.objects.all().order_by("-id")
        serializer = RecipeSerializer(recipes, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_retrieve_recipe_for_only_current_user(self):
        new_user = get_user_model().objects.create_user(
            name = "New test user",
            email="new-test-user@example.com",
            password="newPassword124",
        )
        create_recipe(new_user)
        create_recipe(self.user)
        create_recipe(self.user)
        res = self.client.get(RECIPES_LIST_URL)
        recipes = Recipe.objects.filter(user=self.user).order_by("-id")
        serializer = RecipeSerializer(recipes, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

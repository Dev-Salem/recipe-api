from decimal import Decimal

from core.models import Recipe, Tag
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from recipe.serializers import RecipeSerializer
from rest_framework import status
from rest_framework.test import APIClient

RECIPES_LIST_URL = reverse("recipe:recipe-list")


def recipe_details_url(recipe_id):
    return reverse("recipe:recipe-detail", args=[recipe_id])


def create_recipe(user, **params):
    defaults = {
        "title": "Test Recipe Name",
        "description": "Test Recipe Description..",
        "time_minutes": 12,
        "price": Decimal("3.53"),
    }
    defaults.update(params)
    return Recipe.objects.create(user=user, **defaults)


def create_user(**params):
    """Create and return a new user."""
    return get_user_model().objects.create_user(**params)


class PublicRecipeAPITests(TestCase):
    """Test unauthenticated api requests"""

    def setUp(self):
        self.client = APIClient()

    def test_get_recipe_list_unauthorized(self):
        """Test returning an error when request is unauthorized"""
        res = self.client.get(RECIPES_LIST_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateAPITests(TestCase):
    """Test authenticated api requests"""

    def setUp(self):
        self.user = create_user(email="user@example.com", password="test123")
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
        new_user = create_user(email="user23@example.com", password="test123")
        create_recipe(new_user)
        create_recipe(self.user)
        create_recipe(self.user)
        res = self.client.get(RECIPES_LIST_URL)
        recipes = Recipe.objects.filter(user=self.user).order_by("-id")
        serializer = RecipeSerializer(recipes, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_retrieve_recipe_details(self):
        """Test retrieving recipe details successfully"""
        recipe = create_recipe(user=self.user)
        res = self.client.get(recipe_details_url(recipe.id))
        serializer = RecipeSerializer(recipe, many=False)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_create_recipe_through_endpoint(self):
        """Test creating a recipe successfully through endpoint"""
        payload = {
            "title": "Test Recipe Name",
            "description": "Test Recipe Description..",
            "time_minutes": 12,
            "price": Decimal("3.53"),
        }

        res = self.client.post(RECIPES_LIST_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipe = Recipe.objects.get(id=res.data["id"])

        for k, v in payload.items():
            self.assertEqual(getattr(recipe, k), v)
        self.assertEqual(recipe.user, self.user)

    def test_update_recipe_partial(self):
        recipe = create_recipe(user=self.user)

        res = self.client.patch(
            recipe_details_url(recipe.id), {"title": "updated recipe"}
        )
        recipe = Recipe.objects.get(id=recipe.id)
        serializer = RecipeSerializer(recipe, many=False)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(serializer.data["title"], "updated recipe")

    def test_full_recipe_update(self):
        recipe = create_recipe(user=self.user)
        payload = {
            "title": "updated name",
            "description": "updated description",
            "time_minutes": 25,
            "price": Decimal("4.32"),
        }
        res = self.client.put(recipe_details_url(recipe.id), payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        recipe.refresh_from_db()
        for k, v in payload.items():
            self.assertEqual(getattr(recipe, k), v)
        self.assertEqual(recipe.user, self.user)

    def test_update_user_returns_error(self):
        """Test changing recipe user results in an error"""
        new_user = create_user(email="email@testexample.com", password="112password")
        recipe = create_recipe(self.user)

        res = self.client.patch(recipe_details_url(recipe.id), {"user": new_user.id})

        recipe.refresh_from_db()
        self.assertEqual(recipe.user, self.user)

    def test_delete_recipe(self):
        """Test deleting a recipe"""
        recipe = create_recipe(self.user)

        res = self.client.delete(recipe_details_url(recipe.id))
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Recipe.objects.filter(id=recipe.id).exists())

    def test_delete_other_users_recipe_error(self):
        """Test trying to delete another user recipes gives an error"""
        new_user = create_user(email="self@example.com", password="password1245")
        recipe = create_recipe(new_user)

        res = self.client.delete(recipe_details_url(recipe.id))
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(Recipe.objects.filter(id=recipe.id).exists())

    def test_create_recipe_with_new_tags(self):
        """Test creating a recipe with new tags"""
        payload = {
            "title": "Test Recipe Name",
            "description": "Test Recipe Description..",
            "time_minutes": 12,
            "price": Decimal("3.53"),
            "tags": [{"name": "Savory"}, {"name": "Dinner"}],
        }
        res = self.client.post(RECIPES_LIST_URL, payload, format="json")
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipes = Recipe.objects.filter(user=self.user)
        recipe = recipes[0]
        self.assertEqual(recipes.count(), 1)
        self.assertEqual(recipe.tags.count(), 2)

        for tag in payload["tags"]:
            exists = Tag.objects.filter(name=tag["name"], user=self.user).exists()
            self.assertTrue(exists)

    def test_create_recipe_with_existing_tags(self):
        """Test creating a new recipe that has existing tags"""
        tag_taco = Tag.objects.create(user=self.user, name="Taco")

        payload = {
            "title": "Test Recipe Name",
            "description": "Test Recipe Description..",
            "time_minutes": 12,
            "price": Decimal("3.53"),
            "tags": [
                {"name": "Taco"},
                {"name": "Snack"},
            ],
        }
        res = self.client.post(RECIPES_LIST_URL, payload, format="json")

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipes = Recipe.objects.filter(user=self.user)
        recipe = recipes[0]
        self.assertEqual(recipes.count(), 1)
        self.assertEqual(recipe.tags.count(), 2)
        self.assertIn(tag_taco, recipe.tags.all())
        for tag in payload["tags"]:
            exists = Tag.objects.filter(name=tag["name"], user=self.user).exists()
            self.assertTrue(exists)

    def test_create_tag_on_update(self):
        """Test adding new tags when updating the recipe"""
        recipe = create_recipe(user=self.user)
        payload = {"tags": [{"name": "Savory"}]}
        url = recipe_details_url(recipe.id)
        res = self.client.patch(url, payload, format="json")

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        tags = Tag.objects.get(user=self.user, name="Savory")
        self.assertEqual(recipe.tags.count(), 1)
        self.assertIn(tags, recipe.tags.all())

    def test_update_recipe_assign_tags(self):
        """Test assigning existing tags when updating a recipe"""
        tag_bake = Tag.objects.create(user=self.user, name="Bake")
        recipe = create_recipe(user=self.user)
        recipe.tags.add(tag_bake)

        # have an existing recipe with tags, update to add new tags, previous tags still extending
        tag_coffee = Tag.objects.create(user=self.user, name="Coffee")
        payload = {"tags": [{"name": "Coffee"}]}
        url = recipe_details_url(recipe.id)
        res = self.client.patch(url, payload, format="json")

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn(tag_coffee, recipe.tags.all())
        self.assertNotIn(tag_bake, recipe.tags.all())

    def test_clear_recipe_tags(self):
        tag_bake = Tag.objects.create(user=self.user, name="Bake")
        recipe = create_recipe(user=self.user)
        recipe.tags.add(tag_bake)

        payload = {"tags": []}
        url = recipe_details_url(recipe.id)
        res = self.client.patch(url, payload, format="json")

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(recipe.tags.count(), 0)

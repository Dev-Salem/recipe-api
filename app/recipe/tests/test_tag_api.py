from core.models import Tag
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from recipe.serializers import TagSerializer
from rest_framework import status
from rest_framework.test import APIClient

TAGS_URL = reverse("recipe:tag-list")


def details_url(tag_id):
    return reverse("recipe:tag-detail", args=[tag_id])


def create_user(email="test@example.com", password="testpassword123"):
    """Create and return a new user."""
    return get_user_model().objects.create_user(email=email, password=password)


def detail_url(tag_id):
    """Create and return a tag detail url."""
    return reverse(
        "recipe:tag-detail",
        args=[
            tag_id,
        ],
    )


class PublicTagApiTests(TestCase):
    "Test unauthenticated api requests"

    def setUp(self):
        self.client = APIClient()

    def test_get_recipe_list_unauthorized(self):
        """Test retrieve recipes list for unauthenticated api requests"""
        res = self.client.get(TAGS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateTagApiTests(TestCase):
    """Test authenticated api requests"""

    def setUp(self):
        self.client = APIClient()
        self.user = create_user()
        self.client.force_authenticate(user=self.user)

    def test_retrieve_tags(self):
        """Test getting tags"""
        Tag.objects.create(user=self.user, name="Vegan")
        Tag.objects.create(user=self.user, name="Carnists")

        res = self.client.get(TAGS_URL)
        tags = Tag.objects.all().order_by("-name")
        serializer = TagSerializer(tags, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_retrieve_only_users_tags(self):
        """Test getting only tags that belong to the user"""
        new_user = create_user(email="mytest@example.com")
        tag = Tag.objects.create(user=self.user, name="Savory")
        Tag.objects.create(user=new_user, name="Desert")

        res = self.client.get(TAGS_URL)
        serializer = TagSerializer(tag, many=False)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn(serializer.data, res.data)
        self.assertNotIn("Desert", res.data)

    def test_update_tag(self):
        """Test updating a tag"""
        tag = Tag.objects.create(user=self.user, name="Savory")
        payload = {"name": "Sweet"}
        url = details_url(tag.id)
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        tag.refresh_from_db()
        self.assertEqual(tag.name, payload["name"])

    def test_delete_tag(self):
        """Test deleting a tag"""
        tag = Tag.objects.create(user=self.user, name="Savory")

        res = self.client.delete(details_url(tag.id))
        tag_exists = Tag.objects.filter(id=tag.id).exists()

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)

        self.assertFalse(tag_exists)

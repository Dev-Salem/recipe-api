from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import *

router = DefaultRouter()
router.register("recipes", RecipeViewSet)
router.register(r"tags", TagViewSet, basename="tag")
app_name = "recipe"

urlpatterns = [path("", include(router.urls))]

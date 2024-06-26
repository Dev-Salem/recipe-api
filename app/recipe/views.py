from core.models import Recipe, Tag
from rest_framework import mixins, viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from .serializers import RecipeDetailsSerializer, RecipeSerializer, TagSerializer


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeDetailsSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def get_queryset(self):
        return Recipe.objects.filter(user=self.request.user).order_by("-id")

    def get_serializer_class(self):
        if self.action == "list":
            return RecipeSerializer
        return RecipeDetailsSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class TagViewSet(
    mixins.DestroyModelMixin,
    mixins.UpdateModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def get_queryset(self):
        return Tag.objects.filter(user=self.request.user).order_by("-name")

from rest_framework import viewsets
from core.models import Recipe
from .serializers import RecipeSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def get_queryset(self,):
        return Recipe.objects.filter(user=self.request.user).order_by('-id')



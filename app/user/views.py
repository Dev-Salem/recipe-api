from django.shortcuts import render
from rest_framework import generics
from .serializers import UserSerializers, AuthTokenSerializer
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.settings import api_settings
class CreateUserView(generics.CreateAPIView):
    serializer_class = UserSerializers

class CreateTokenView(ObtainAuthToken):
    '''Create a new auth token for the user'''
    serializer_class = AuthTokenSerializer
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES
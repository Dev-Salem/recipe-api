from django.shortcuts import render
from rest_framework import generics
from .serializers import UserSerializers


class UserCreateAPIView(generics.CreateAPIView):
    serializer_class = UserSerializers

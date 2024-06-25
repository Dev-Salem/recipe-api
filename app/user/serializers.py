'''Serializers for the user model'''
from rest_framework import serializers
from django.contrib.auth import get_user_model

class UserSerializers(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ('email','password','name')
        extra_kwargs = {'password':{'write_only':True,'min_length':6}}
    
    def create(self, validated_data):
        '''Create and return a use with encrypted password'''
        return get_user_model().objects.create_user(**validated_data)
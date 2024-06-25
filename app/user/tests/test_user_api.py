'''
Tests for the user API
'''
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from rest_framework import status
from rest_framework.test import APIClient

CREATE_USER_URL = reverse("user:create")

def create_user(**params):
    '''
    Create and return a  user
    '''
    return get_user_model().objects.create_user(**params)

class PublicUserApiTests(TestCase):
    def setUP(self):
        self.client = APIClient()
    
    def test_create_user_is_success(self):
        '''Test creating a user successfully'''
        payload = {
            'email':'test@example.com',
            'password':'testpassword',
            'name':'Test User Name'
        }
        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        user = get_user_model().objects.get(email=payload['email'])
        self.assertTrue(user.check_password(payload['password']))
        self.assertNotIn('password',res.data)
    
    def test_password_too_short_error(self):
        '''Test returning an error when the password is too short'''
        payload = {
            'email':'te23st@example.com',
            'password':'sda',
            'name':'Test User Name'
        }
        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        user_exists = get_user_model().objects.filter(email=payload['email']).exists()
        self.assertFalse(user_exists)
    
    def test_user_create_user_with_same_email(self):
        '''Test returning an error when the user already exists'''
        payload = {
            'email':'test@example.com',
            'password':'testpassword',
            'name':'Test User Name'
        }
        create_user(**payload)
        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        user = get_user_model().objects.get(email=payload['email'])
        self.assertEqual(user.email, payload['email'])
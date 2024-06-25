'''
Tests for the user API
'''
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from rest_framework import status
from rest_framework.test import APIClient

CREATE_USER_URL = reverse("user:create")
USER_TOKEN_URL = reverse("user:token")
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
    
    def test_create_toke_for_user(self):
        ''''Test generate a toke when user sign in successfully'''
        # register the user
        user = {
            'name':'Test User Name',
            'email':'testy@example.co',
            'password':'testpassword2'
        }
        create_user(**user)
        #sign in the user using token endpoint
        res = self.client.post(USER_TOKEN_URL,{
            'email':user['email'],
            'password':user['password']
        })

        #check if the result has token in it and it's 200
        self.assertIn('token',res.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
    
    def test_return_error_when_sign_in_fail(self):
        '''Test returning an error when user enters invalid credentials'''
        # register the user
        user = {
            'name':'Test User Name',
            'email':'testy@example.co',
            'password':'testpassword2'
        }
        create_user(**user)
        #try to sign in the user using token endpoint with invalid email
        res = self.client.post(USER_TOKEN_URL,{
            'email':'doesnotexit@example.com',
            'password':user['password']
        })

        #check if the result does not have token in it and it's 400
        self.assertNotIn('token',res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_create_token_blank_password(self):
        '''Test returning an error when user enters blank password'''
        user = {
            'name':'Test User Name',
            'email':'testy@example.co',
            'password':'testpassword2'
        }
        create_user(**user)
        
        payload ={
            'email':user['email'],
            'password':''
        }
        res = self.client.post(USER_TOKEN_URL,payload)

        self.assertNotIn('token',res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
'''Test admin model'''
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import Client

class AdminSiteTests(TestCase):
    def setUp(self):
        '''Create user and client'''
        self.superuser = get_user_model().objects.create_superuser(
            email='admin@example.com',
            password='password123'
        )
        self.client = Client()
        self.client.force_login(self.superuser)
        self.user= get_user_model().objects.create_user(
            email='user@example.com',
            password='pass1234567'
        )
    
    def test_users_list(self):
        '''Test users are listed on the admin site'''
        url = reverse('admin:core_user_changelist')
        res = self.client.get(url)
        self.assertContains(res, self.user.name)
        self.assertContains(res, self.user.email)
    
    def test_edit_user_page_available(self):
        '''Test edit user page returns 200 status code'''
        url = reverse('admin:core_user_change',args=[self.user.id])
        res = self.client.get(url)
        self.assertEqual(res.status_code, 200)
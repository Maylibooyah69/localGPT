from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

CREATE_USER_URL = reverse('user:create')


def create_user(**params):
    """Helper function to create a new user"""
    return get_user_model().objects.create_user(**params)


class PublicUserApiTests(TestCase):
    """Test the users API (public)"""

    def setUp(self):
        self.client = APIClient()

    def test_create_valid_user_success(self):
        """Test creating user with valid payload is successful"""
        payload = {
            'email': 'dummy@example.com',
            'password': 'dummy_password',
            'username': 'Dummy_User' #username may not contain spaces
        }
        response = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        user = get_user_model().objects.get(**response.data)
        self.assertTrue(user.check_password(payload['password']))
        self.assertNotIn('password', response.data)

    def test_user_with_email_exists_error(self):
        """Test creating a user with an existing email returns an error"""
        payload = {
            'email': 'existing@example.com',
            'password': 'existing_password',
            'username': 'Existing User'
        }
        create_user(**payload)

        response = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_with_short_password_error(self):
        """Test creating a user with a password less than 8 characters returns an error"""
        payload = {
            'email': 'test@example.com',
            'password': 'short',
            'username': 'Test name', }
        response = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(get_user_model().objects.filter(
            email=payload['email']).exists())

from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import AuthSerializer

User = get_user_model()

class TestAuthAPI(APITestCase):
    def setUp(self):
        try:
            self.url = reverse('auth')
        except:
            self.url = 'auth/'

    def test_register_creates_new_user_and_returns_tokens(self):
        data = {'username': 'newuser', 'password': 'password123'}
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        user = User.objects.filter(username='newuser').first()
        self.assertIsNotNone(user)
        self.assertTrue(user.check_password('password123'))

    def test_login_existing_user_with_correct_credentials(self):
        user = User.objects.create(username='existing')
        user.set_password('secret')
        user.save()
        data = {'username': 'existing', 'password': 'secret'}
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_login_existing_user_with_incorrect_credentials(self):
        user = User.objects.create(username='wrongpass')
        user.set_password('rightpass')
        user.save()
        data = {'username': 'wrongpass', 'password': 'wrongpass'}
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        self.assertTrue(
            'non_field_errors' in response.data or
            'detail' in response.data or
            'password' in response.data
        )

    def test_missing_fields_returns_error(self):
        response = self.client.post(self.url, {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('username', response.data)
        self.assertIn('password', response.data)

class TestAuthSerializer(APITestCase):
    def test_validate_new_user_creates_user(self):
        data = {'username': 'serializer_new', 'password': 'pass1234'}
        serializer = AuthSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        user = User.objects.filter(username='serializer_new').first()
        self.assertIsNotNone(user)
        self.assertTrue(user.check_password('pass1234'))
        validated = serializer.validated_data
        self.assertEqual(validated['user'], user)

    def test_validate_existing_user_wrong_password(self):
        user = User.objects.create(username='serializer_exist')
        user.set_password('correct')
        user.save()
        data = {'username': 'serializer_exist', 'password': 'wrong'}
        serializer = AuthSerializer(data=data)
        with self.assertRaises(Exception):
            serializer.is_valid(raise_exception=True)

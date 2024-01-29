from rest_framework.test import APITestCase, override_settings
from rest_framework_simplejwt.tokens import RefreshToken
from django.urls import reverse
from tests.accounts.factories import UserFactory
from django.contrib.auth import get_user_model
from unittest import mock
from mimi.accounts.mails.tokens import account_activation_token
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from mimi.accounts.models import BlockedList


User  = get_user_model()

class TestRegistrationAPIView(APITestCase):
    
    def setUp(self):
        self.maxDiff = None
        self.url = reverse('accounts_api_v1:registration')
        
    

    @override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
    def test_registration_of_user_with_valid_data(self):
        """ Test account is created with valid data"""
        valid_data = {
            'first_name': 'james',
            'email': 'james@mail.com',
            'address': 'lagos',
            'gender': 'Male',
            'bio': 'I love Myself',
            'password': '1234455644',
            'username': 'james'
        }

        request_data = {
            'HTTP_HOST': 'localhost:8000'
        }
        with mock.patch('mimi.accounts.api.v1.serializers.account_activation.send_activation_email') as mock_send_email:
            response = self.client.post(self.url, valid_data, format='json', **request_data)
 
        
        self.assertEqual(response.status_code, 201)
        user = User.objects.filter(email=valid_data['email']).first()
        
        self.assertIsNotNone(user)
        self.assertEqual(user.first_name, valid_data['first_name'])
        self.assertNotEqual(user.password, valid_data['password'])
        self.assertEqual(user.is_active, False)
        
        mock_send_email.assert_called_once_with(user, request_data['HTTP_HOST'])
        # self.assertIn('Activate your account', console_output)
        # console_output = mail.outbox[0].message().as_string()
        

       
    def test_registration_of_user_with_invalid_data(self):
        """ Test account is not created with invalid data"""
        
        invalid_data = {
            'first_name': 'james',
            'email': 'james@mail.com',
            'address': 'lagos',
            'gender': 'Male',
            'bio': 'I love Myself',
            'password': '1234'
        }

        request_data = {
            'HTTP_HOST': 'localhost:8000'
        }
        response = self.client.post(self.url, invalid_data, format='json', **request_data)
        
        self.assertEqual(response.status_code, 400)
        self.assertIsNone(User.objects.filter(email=invalid_data['email']).first())

    def test_account_is_not_created_when_email_exists(self):

        """Test account cannot be created when email exists already"""
        
        existing_user = UserFactory()
        
        invalid_data = {
            'first_name': 'james',
            'email': 'delight@gmail.com',
            'address': 'lagos',
            'gender': 'Male',
            'bio': 'I love Myself',
            'password': '123456789',
            'username': 'jamesguy'
        }

        request_data = {
            'HTTP_HOST': 'localhost:8000'
        }

        response = self.client.post(self.url, invalid_data, format='json', **request_data)
        self.assertEqual(response.status_code, 400)
        self.assertIsNone(User.objects.filter(email=invalid_data['username']).first())




class TestActivationAccountAPIView(APITestCase):

    def setUp(self):
        self.maxDiff = None
        self.user = UserFactory()
    
    def test_activation_of_account_with_valid_token_and_uid(self):
        """Actvation of account with valid token and uid"""

        token = account_activation_token.make_token(self.user)
        uid = urlsafe_base64_encode(force_bytes(self.user.id))
        activation_url = reverse('accounts_api_v1:activate', args=[uid, token])

        response = self.client.get(activation_url)

        self.user.refresh_from_db()
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.user.is_active, True)

    def test_activation_of_account_with_invalid_token_and_uid(self):
        """Actvation of account with invalid token and invalid uid"""

        bad_token = account_activation_token.make_token(self.user) + ' '
        uid = urlsafe_base64_encode(force_bytes(self.user.id))
        activation_url = reverse('accounts_api_v1:activate', args=[uid, bad_token])

        response = self.client.get(activation_url)

        self.user.refresh_from_db()
        
        self.assertEqual(response.status_code, 400)
        self.assertEqual(self.user.is_active, False)
    


class TestSignInAPIView(APITestCase):

    def setUp(self):
        self.url = reverse('accounts_api_v1:sign_in')
        self.active_user = UserFactory(is_active=True, username='active')
        self.inactive_user = UserFactory(email='inactive@gmail.com')

    
    def test_user_with_active_account_can_sign_in_with_valid_credentials(self):
        """Test user with active account can sign in using valid credentials"""
        
        valid_data = {
            'email': self.active_user.email,
            'password': self.active_user.password
        }
        self.active_user.set_password(valid_data['password'])
        self.active_user.save()

        response = self.client.post(self.url, valid_data, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertIn('access_token', response.data)
    
    
    def test_user_with_active_account_cannot_sign_in_with_invalid_credentials(self):
        """Test user with active account can sign in using invalid credentials"""
        
        invalid_data = {
            'email': self.active_user.email,
            'password': "password"
        }
        
        response = self.client.post(self.url, invalid_data, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertIn('credential_error', response.data)
    
     
    def test_user_with_inactive_account_cannot_sign_in_with_valid_credentials(self):
        """Test user with inactive account can sign in using invalid credentials"""
        
        invalid_data = {
            'email': self.inactive_user.email,
            'password': self.inactive_user.password
        }
        
        response = self.client.post(self.url, invalid_data, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertIn('credential_error', response.data)


class TestBlockUserAPIView(APITestCase):

    def setUp(self):
        self.user1 = UserFactory(is_active=True)
        self.user2 = UserFactory(username='user1', email='user1@mail.com', is_active=True)
        self.url = reverse('accounts_api_v1:block_user')
    
    def test_authorized_user_can_block_other_user(self):
        """Test authorized user can block other user"""
        authorization_token = RefreshToken.for_user(self.user1).access_token

        headers = {'HTTP_AUTHORIZATION': f'Bearer {authorization_token}'}

        valid_data = {
            'blocked_user': self.user2.id
        }

        response = self.client.post(self.url, valid_data, format='json', **headers)
        self.assertEqual(response.status_code, 201)
        self.assertTrue(
            BlockedList.objects.filter(user=self.user1, blocked_user=self.user2)
        )

    
    def test_unauthorized_user_cannot_block_other_user(self):
        """Test unauthorized user cannot block other user"""
        
        valid_data = {
            'blocked_user': self.user2.id
        }

        response = self.client.post(self.url, valid_data, format='json')
        self.assertEqual(response.status_code, 401)
        self.assertFalse(
            BlockedList.objects.filter(user=self.user1, blocked_user=self.user2)
        )



class TestChangeAPIView(APITestCase):

    def setUp(self):
        self.url = reverse('accounts_api_v1:change_password')
        self.user = UserFactory(is_active=True)

    
    def test_authorized_user_can_change_their_password(self):
        """Test authorized user can change their password"""










    
    

    


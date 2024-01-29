from rest_framework_simplejwt.tokens import RefreshToken
from django.urls import reverse
from tests.chats.factories import (
    RoomFactory, 
    RoomMembersFactory, 
    JoinRoomRequestsFactory,
)
from tests.accounts.factories import UserFactory
from rest_framework.test import APITestCase
from  mimi.chats.models import Room, RoomMembers, JoinRoomRequests
from django.contrib.auth import get_user_model

User = get_user_model()


class TestRoomAPIView(APITestCase):

    def setUp(self):
        self.maxDiff = None
        self.url = reverse('chats_api_v1:list_or_create_room')
        self.user = UserFactory(is_active=True)
        
    def test_creation_of_room_by_authenticated_user(self):
        """Test to create room by an authenticated user"""

        authorization_token = RefreshToken.for_user(self.user).access_token
        headers = {'HTTP_AUTHORIZATION': f'Bearer {authorization_token}'}
        
        valid_data = {
            'room_name': "ROOM 1",
            'number_of_persons': "10",
            'description': "We play a lot"
        }

        response = self.client.post(self.url, valid_data, format='json', **headers)
        
        self.assertEqual(response.status_code, 201)
        self.assertTrue(Room.objects.filter(room_name=valid_data['room_name']).exists())
        self.assertEqual(Room.objects.filter().first().room_name, valid_data['room_name'])
        self.assertEqual(Room.objects.filter().first().room_creator_id, str(self.user.id))
        room_creator_username = User.objects.filter(id=self.user.id).first().username
        self.assertEqual(room_creator_username,"delight" )
    
    def test_noncreation_of_room_by_unauthenticated_user(self):
        """Test to not create room by an unauthenticated user"""

        
        invalid_data = {
            'room_name': "ROOM 2",
            'number_of_persons': "10",
            'description': "We play a lot"
        }

        response = self.client.post(self.url, invalid_data, format='json')
    
        self.assertEqual(response.status_code, 401)
        self.assertFalse(Room.objects.filter(room_name=invalid_data['room_name']).exists())
    


    def test_room_name_is_unique_stands(self):
        """Test room name can be unique only"""

        authorization_token = RefreshToken.for_user(self.user).access_token
        headers = {'HTTP_AUTHORIZATION': f'Bearer {authorization_token}'}
        
        existing_room  = RoomFactory()

        invalid_data = {
            'room_name': "UNIQUE ROOM",
            'number_of_persons': "10",
            'description': "We play a lot"
        }

        response = self.client.post(self.url, invalid_data, **headers)
        self.assertEqual(response.status_code, 400)
    
        self.assertEqual(response.json()['error'][0], f'room {invalid_data['room_name']} exists.')
        self.assertNotEqual(Room.objects.filter(room_name=invalid_data['room_name']).count(), 2)
        
    
    def test_public_rooms_can_be_retrieved_by_authenticated_user(self):
        """Test public rooms can only be retrieved by authenticated user"""
        
        user = UserFactory(email='user@mail.com', username='user')
        room_1 = RoomFactory(room_creator_id=user.id, room_name="ROOM 1", is_public=True, number_of_persons=20)
        room_2 = RoomFactory(room_creator_id=user.id, room_name="ROOM 2", is_public=True, number_of_persons=10)
        room_3 = RoomFactory(room_creator_id=user.id, room_name="ROOM 3", is_public=False)
    
        authorization_token = RefreshToken.for_user(self.user).access_token
        headers = {'HTTP_AUTHORIZATION': f'Bearer {authorization_token}'}
        expected_data = [
                {
                    'id': str(room_1.id),
                    'room_name': room_1.room_name, 
                    'description': room_1.description, 
                    'number_of_persons': room_1.number_of_persons
                 }, 
                {
                    'id': str(room_2.id),
                    'room_name': room_2.room_name, 
                    'description': room_2.description, 
                    'number_of_persons': room_2.number_of_persons
                }
            ]
        

        response = self.client.get(self.url, **headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), expected_data)



class TestEditOrDeleteRoomAPIView(APITestCase):

    def setUp(self):
        self.user = UserFactory(is_active=True)
        self.user2 = UserFactory(email='mimi@mail.com', is_active=True, username='mimi')

        


    def test_admin_of_room_can_edit_room_details(self):
        """Test admin of room can edit room details like description, and number_of_persons, alone"""
        room = RoomFactory(room_creator_id=str(self.user.id), room_name="SPECIAL ROOM")
        room_member = RoomMembersFactory(is_admin=True, room=room, room_members=self.user)

        url = reverse('chats_api_v1:edit_or_delete_room', args=[room.room_name])
        valid_data = {
            'room_name': "SPECIAL ROOM FOR ALL",
            'number_of_persons': 10
        }
        authorization_token = RefreshToken.for_user(self.user).access_token
        headers = {'HTTP_AUTHORIZATION': f'Bearer {authorization_token}'}
        
        response = self.client.put(url, valid_data,**headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Room.objects.filter(id=room.id).first().room_name, valid_data['room_name'])

    
    def test_nonadmin_of_room_can_edit_cannot_room_details(self):
        """Test nonadmin of room cannot edit room details like description, and number_of_persons, alone"""
        room = RoomFactory(room_creator_id=str(self.user), room_name="SPECIAL ROOM")
        room_member = RoomMembersFactory(is_admin=True, room=room, room_members=self.user)
        user2 = UserFactory(is_active=True, email='user2.mail.com', username='user2')
        
        url = reverse('chats_api_v1:edit_or_delete_room', args=[room.room_name])
        invalid_data = {
            'room_name': "SPECIAL ROOM FOR ALL",
            'number_of_persons': 10
        }

        authorization_token = RefreshToken.for_user(user2).access_token
        headers = {'HTTP_AUTHORIZATION': f'Bearer {authorization_token}'}
        
        response = self.client.put(url, invalid_data,**headers)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(Room.objects.filter(id=room.id).first().room_name, room.room_name)

    

    def test_admin_can_delete_created_room(self): # NOTE: TEST MUST BE RE-WRITTEN, ROOM DELETION MUST BE APPROVED BY WHOLE ADMINS
        """Test admin can delete room"""

        room = RoomFactory(room_creator_id=str(self.user.id), room_name="SPECIAL ROOM")
        room_member = RoomMembersFactory(is_admin=True, room=room, room_members=self.user)

        authorization_token = RefreshToken.for_user(self.user).access_token
        headers = {'HTTP_AUTHORIZATION': f'Bearer {authorization_token}'}
        
        url = reverse('chats_api_v1:edit_or_delete_room', args=[room.room_name])
        response = self.client.delete(url, **headers)
        self.assertEqual(response.status_code, 204)
        self.assertIsNone(Room.objects.filter(room_name=room.room_name).first())
        self.assertEqual(RoomMembers.objects.filter(room=room).first(), None)


class TestUserRoomRequestAPIView(APITestCase):

    def setUp(self):
        self.url = reverse('chats_api_v1:user_room_request')
        self.user = UserFactory(is_active=True)
        self.room = RoomFactory()


    def authenticated_user_can_send_room_request(self):
        """Test authenticated user can send room request"""

        authorization_token = RefreshToken.for_user(self.user).access_token
        headers = {'HTTP_AUTHORIZATION': f'Bearer {authorization_token}'}

        valid_data = {
            'room': self.room.id,
            'room_request': 0
        }

        response = self.client.post(self.url, data=valid_data, **headers)
        self.assertTrue(response.status_code, 201)
        self.assertTrue(JoinRoomRequests.objects.filter(user=self.user, room=self.room).exists())


    def test_user_cannot_send_room_request_multiple_times(self):
        """Test User cannot send room request if sent before"""
        
        JoinRoomRequestsFactory(
            user=self.user,
            room=self.room
        )
        
        authorization_token = RefreshToken.for_user(self.user).access_token
        headers = {'HTTP_AUTHORIZATION': f'Bearer {authorization_token}'}

        valid_data = {
            'room': self.room.id,
            'room_request': 0
        }

        response = self.client.post(self.url, data=valid_data, **headers)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(JoinRoomRequests.objects.filter(room=self.room, user=self.user).count(), 1)
    
    def test_unauthenticated_user_cannot_send_room_request(self):
        """Test unauthenticated user can send room request"""

        invalid_data = {
            'room': self.room.id,
            'room_request': 0
        }

        response = self.client.post(self.url, data=invalid_data)

        self.assertEqual(response.status_code, 401)
    
    def test_authenticated_user_can_retrieve_all_friend_requests(self):
        """Test authenticated can retrieve all sent room requests"""

        room_1 = RoomFactory(room_creator_id=self.user.id, room_name="ROOM 1")
        room_2 = RoomFactory(room_creator_id=self.user.id, room_name="ROOM 2")

        user = UserFactory(is_active=True, username='user', email='user@mail.com')

        room_request_1 = JoinRoomRequestsFactory(
            user = user,
            room = room_1,
            room_request = 0 
        )
        room_request_2 = JoinRoomRequestsFactory(
            user = user,
            room = room_2,
            room_request = 0
        )

        expected_data =  [
            {
                'room_name': room_1.room_name,
                'room': str(room_1.id), 
                'room_request': 0
            },
            
            {
                'room_name': room_2.room_name,
                'room': str(room_2.id), 
                'room_request': 0
               
            }

            ]
            


        
        authorization_token = RefreshToken.for_user(user).access_token
        headers = {'HTTP_AUTHORIZATION': f'Bearer {authorization_token}'}

        response = self.client.get(self.url, **headers)
        self.assertEqual(response.status_code, 200)
        self.assertListEqual(response.json(), expected_data)










        
        
    





# NOTE: STOPPED AT 8
        
        

       

        




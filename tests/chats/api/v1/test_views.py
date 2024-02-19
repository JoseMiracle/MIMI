from rest_framework_simplejwt.tokens import RefreshToken
from django.urls import reverse
from tests.chats.factories import (
    RoomFactory, 
    RoomMembersFactory, 
    JoinRoomRequestsFactory,
)
from mimi.chats.utils.constants import REJECT_ROOM_REQUEST, ACCEPTED_ROOM_REQUEST

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
        room_member_as_admin = RoomMembersFactory(is_admin=True, room=room, room_member=self.user)

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
        room_member_as_admin = RoomMembersFactory(is_admin=True, room=room, room_member=self.user)
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
        room_member_as_admin = RoomMembersFactory(is_admin=True, room=room, room_member=self.user)

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


class TestAcceptOrRejectUserRoomRequestAPIView(APITestCase):
    
    def setUp(self):
        self.admin = UserFactory(is_active=True, username='admin', email='admin@mail.com')
        self.room = RoomFactory()
        self.room_member = RoomMembersFactory(is_admin=True, room=self.room, room_member=self.admin)

    
    def test_admin_can_reject_user_room_request(self):
        """Test admin can reject user room request"""
        user = UserFactory(is_active=True)
       
        user_room_request = JoinRoomRequestsFactory(
            room=self.room,
            user=user,
        )
        

        url = reverse('chats_api_v1:accept_or_reject_room_request', args=[self.room.room_name, user_room_request.id])
        data = {
            'decision': REJECT_ROOM_REQUEST
        }
        authorization_token = RefreshToken.for_user(self.admin).access_token
        headers = {'HTTP_AUTHORIZATION': f'Bearer {authorization_token}'}
        
        response = self.client.put(url, data=data, format='json', **headers)
        user_friend_request_obj = JoinRoomRequests.objects.filter(room=self.room, user=user).first()
        self.assertEqual(response.status_code, 200)
        self.assertIsNone(user_friend_request_obj)
        self.assertEqual(RoomMembers.objects.count(), 1) 
    
    def test_admin_of_another_room_cannot_reject_or_accept_room_request_of_another_room(self):
        """Test admin of another room cannot accept or reject or accept the room request of another room"""

        other_room_admin = UserFactory(is_active=True, username='other_admin', email='other_room_admin@mail.com')
        other_room  = RoomFactory(room_creator_id=other_room_admin.id, room_name="OTHER USER ROOM")
        other_room_member = RoomMembersFactory(is_admin=True, room=other_room, room_member=other_room_admin)

        user = UserFactory(is_active=True, username='sender', email='sender@mail.com')
        user_room_request = JoinRoomRequestsFactory(
            room=self.room, 
            user=user,
        )


        authorization_token = RefreshToken.for_user(other_room_admin).access_token
        headers = {'HTTP_AUTHORIZATION': f'Bearer {authorization_token}'}
        url = reverse('chats_api_v1:accept_or_reject_room_request', args=[self.room.room_name, user_room_request.id])
        data = {
            'decision': REJECT_ROOM_REQUEST
        }
        
        response = self.client.put(url, data=data , format='json', **headers)
        self.assertEqual(response.status_code, 403)

    def test_admin_can_accept_room_request_of_a_user(self):
        """Test an admin can accept room request of a user"""

        user = UserFactory(is_active=True)
       
        user_room_request = JoinRoomRequestsFactory(
            room=self.room,
            user=user,
        )
        

        url = reverse('chats_api_v1:accept_or_reject_room_request', args=[self.room.room_name, user_room_request.id])
        data = {
            'decision': ACCEPTED_ROOM_REQUEST
        }
        authorization_token = RefreshToken.for_user(self.admin).access_token
        headers = {'HTTP_AUTHORIZATION': f'Bearer {authorization_token}'}
        
        response = self.client.put(url, data=data, format='json', **headers)
        user_friend_request_obj = JoinRoomRequests.objects.filter(room=self.room, user=user).first()
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(user_friend_request_obj)
        self.assertEqual(JoinRoomRequests.objects.filter(room=self.room, user=user).first().room_request, str(ACCEPTED_ROOM_REQUEST))
        self.assertEqual(RoomMembers.objects.count(), 2)



class TestUserRoomsAPIView(APITestCase):
    
    def setUp(self):
        self.user = UserFactory(is_active=True)
        self.url = reverse('chats_api_v1:user_rooms')
        self.room_1 = RoomFactory(room_name='ROOM 1')
        self.room_2 = RoomFactory(room_name='ROOM 2')
        self.room_3 = RoomFactory(room_name='ROOM 3')

    def test_authenticted_user_can_get_all_rooms_they_belong(self):
        """Test authenticated user can get the room the belong to"""

        authorization_token = RefreshToken.for_user(self.user).access_token
        headers = {'HTTP_AUTHORIZATION': f'Bearer {authorization_token}'}
        joined_room_1 = JoinRoomRequestsFactory(room=self.room_1, user=self.user, room_request=ACCEPTED_ROOM_REQUEST)
        joined_room_2 = JoinRoomRequestsFactory(room=self.room_2, user=self.user, room_request=ACCEPTED_ROOM_REQUEST)
        joined_room_2 = JoinRoomRequestsFactory(room=self.room_3, user=self.user, room_request=ACCEPTED_ROOM_REQUEST)

        response = self.client.get(self.url, **headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), JoinRoomRequests.objects.filter(user=self.user, room_request=ACCEPTED_ROOM_REQUEST).count())


    def test_unauthenticated_user_cannot_get_rooms_they_belong(self):
        """Test unauthenticated user cannot get the rooms they belong"""
        joined_room_1 = JoinRoomRequestsFactory(room=self.room_1, user=self.user, room_request=ACCEPTED_ROOM_REQUEST)
        joined_room_2 = JoinRoomRequestsFactory(room=self.room_2, user=self.user, room_request=ACCEPTED_ROOM_REQUEST)
        joined_room_2 = JoinRoomRequestsFactory(room=self.room_3, user=self.user, room_request=ACCEPTED_ROOM_REQUEST)

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 401)
        self.assertIn(response.json()['detail'], 'Authentication credentials were not provided.')


class TestGetAllUsersInTheRoomAPIView(APITestCase):

    def setUp(self):
        self.user = UserFactory(is_active=True)
        self.room = RoomFactory()
        self.user1 = UserFactory(is_active=True, username='user1', email='user1@mail.com')
        self.user2 = UserFactory(is_active=True, username='user2', email='user2@mail.com')
        self.user3 = UserFactory(is_active=True, username='user3', email='user3@mail.com')

       
        
    def test_authenticated_user_in_the_room_they_belong_can_get_the_users_in_the_room(self):
        """Test user can get all users in a room"""
        room_member = RoomMembersFactory(room=self.room, room_member=self.user)
        room_member1 = RoomMembersFactory(room=self.room, room_member=self.user1)
        room_member2 = RoomMembersFactory(room=self.room, room_member=self.user2)
        room_member3 = RoomMembersFactory(room=self.room, room_member=self.user3)
        
        url = reverse('chats_api_v1:get_user_in_room', args=[self.room.room_name])
        authorization_token = RefreshToken.for_user(self.user).access_token
        
        headers = {'HTTP_AUTHORIZATION': f'Bearer {authorization_token}'}
        response = self.client.get(url, **headers )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), RoomMembers.objects.count())

    

    def test_authenticated_user_not_in_a_room_cannot_get_users_in_that_room(self):
        """Test User from another cannot get users in that room"""
        user_room = RoomFactory(room_name="USER NEW ROOM")
        other_room = RoomFactory(room_name="OTHER ROOM")
        
        
        room_member = RoomMembersFactory(room=user_room, room_member=self.user)
        other_room_member1 = RoomMembersFactory(room=other_room, room_member=self.user1)
        other_room_member2 = RoomMembersFactory(room=other_room, room_member=self.user2)
        other_room_member3 = RoomMembersFactory(room=other_room, room_member=self.user3)

        url = reverse('chats_api_v1:get_user_in_room', args=[other_room.room_name])
        authorization_token = RefreshToken.for_user(self.user).access_token
        headers = {'HTTP_AUTHORIZATION': f'Bearer {authorization_token}'}
        response = self.client.get(url, **headers)
        self.assertEqual(response.status_code, 400)
        self.assertIn("you don't belong", response.json()['error'])
       
        

class TestRemoveUserFromARoomAPIView(APITestCase):

    def setUp(self):
        self.admin = UserFactory(is_active=True)
        self.room = RoomFactory()
        self.room_member = RoomMembersFactory(room_member=self.admin, room=self.room, is_admin=True)


    def test_authenticated_admin_of_room_can_remove_a_user(self):
        """Test authenticated admin of room can remove a room member"""
        user = UserFactory(is_active=True, username='user', email='user@mail.com')
        user_joined_room = JoinRoomRequestsFactory(room=self.room, user=user, room_request=ACCEPTED_ROOM_REQUEST)
        room = RoomMembersFactory(room=self.room, room_member=user)
        
        url = reverse('chats_api_v1:remove_user_from_room', args=[self.room.room_name, user.username])
        authorization_token = RefreshToken.for_user(self.admin).access_token
        headers = {'HTTP_AUTHORIZATION': f'Bearer {authorization_token}'}
        response = self.client.post(url, format='json', **headers)
        
        self.assertEqual(response.status_code, 200)
        self.assertIsNone(RoomMembers.objects.filter(room=self.room, room_member=user).first())
        self.assertIsNone(JoinRoomRequests.objects.filter(room=self.room, user=user).first())
    
    def test_unauthenticated__admin_of_room_can_remove_a_user(self):
        """Test authenticated admin of room can remove a room member"""
        user = UserFactory(is_active=True, username='user', email='user@mail.com')
        user_joined_room = JoinRoomRequestsFactory(room=self.room, user=user, room_request=ACCEPTED_ROOM_REQUEST)
        room = RoomMembersFactory(room=self.room, room_member=user)
        
        url = reverse('chats_api_v1:remove_user_from_room', args=[self.room.room_name, user.username])
 
        response = self.client.post(url, format='json')
        self.assertEqual(response.status_code, 401)
        self.assertIsNotNone(RoomMembers.objects.filter(room=self.room, room_member=user).first())
        self.assertIsNotNone(JoinRoomRequests.objects.filter(room=self.room, user=user).first())

    def test_admin_from_another_room_cannot_remove_a_user_in_their_room(self):
        """"Test admin fromm am=nother room cannnot remove a user not in their room"""
        another_room_admin = UserFactory(is_active=True, username='another_room_admin', email='anotheroomadmin@mail.com')
        another_room = RoomFactory(room_name="ANOTHER ROOM")
        another_room_member = RoomMembersFactory(room_member=another_room_admin, room=another_room, is_admin=True)
        
        
        user = UserFactory(is_active=True, username='user', email='user@mail.com')
        user_accepted_room_request = JoinRoomRequestsFactory(room=self.room, user=user, room_request=ACCEPTED_ROOM_REQUEST)
        room_member = RoomMembersFactory(room=self.room, room_member=user)


        url = reverse('chats_api_v1:remove_user_from_room', args=[self.room.room_name, user.username])

        authorization_token = RefreshToken.for_user(another_room_admin).access_token
        headers = {'HTTP_AUTHORIZATION': f'Bearer {authorization_token}'}
        response = self.client.post(url, format='json', **headers)
        self.assertEqual(response.status_code, 403)
        self.assertIn("Not a member of the room or room doesn't exist", response.json()['detail'])
        self.assertIsNotNone(user_accepted_room_request)

        

class TestUserLeaveRoomAPIView(APITestCase):

    def setUp(self):
        self.user = UserFactory(is_active=True)
        self.room = RoomFactory()
        self.room_request_by_user = JoinRoomRequestsFactory(room=self.room, user=self.user, room_request=ACCEPTED_ROOM_REQUEST)
        self.room_member = RoomMembersFactory(room=self.room, room_member=self.user)
        self.url = reverse('chats_api_v1:user_leave_room', args=[self.room.room_name])


    def test_authenticated_user_can_leave_room_they_joined(self):
        """Test user can leave room they joined"""
        authorization_token = RefreshToken.for_user(self.user).access_token
        headers = {'HTTP_AUTHORIZATION': f'Bearer {authorization_token}'}
        response = self.client.post(self.url, format='json', **headers)
        self.assertEqual(response.status_code, 200 )
        self.assertIsNone(RoomMembers.objects.filter(room=self.room, room_member=self.user).first())
    
    def test_unauthenticated_user_cannot_leave_room_they_joined(self):
        """Test user can leave room they joined"""
        response = self.client.post(self.url, format='json')
        self.assertEqual(response.status_code, 401)
    
    def test_another_user_cannot_remove_user_from_another_room(self):
        """Test another user cannot remove user from another room"""
        another_user = UserFactory(is_active=True, username='another_user', email='anotheruser@mail.com')
        authorization_token = RefreshToken.for_user(another_user).access_token
        headers = {'HTTP_AUTHORIZATION': f'Bearer {authorization_token}'}
        
        response = self.client.post(self.url, format='json', **headers)
        self.assertEqual(response.status_code, 400)
        self.assertIsNotNone(RoomMembers.objects.filter(room=self.room, room_member=self.user).first())
        






        
    
    







        
        
    





# NOTE: STOPPED AT 8
        
        

       

        




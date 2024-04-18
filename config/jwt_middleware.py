from rest_framework_simplejwt.tokens import AccessToken
from channels.db import database_sync_to_async
from channels.middleware import BaseMiddleware


import logging
logger = logging.getLogger(__name__)

class JWTAuthMiddleware(BaseMiddleware):
    
    async def __call__(self, scope, receive, send):
    
        token = self.get_token_from_scope(scope)
        
        if token != None:
            user = await self.get_user_from_token(token) 
            if user:
                scope['user'] = user

            else:
                scope['error'] = 'User not Found'

        if token == None:
            scope['error'] = 'Provide an auth token'    
    
                
        return await super().__call__(scope, receive, send)

    def get_token_from_scope(self, scope):
        # Extract token from the scope (modify based on your actual implementation)
        headers = dict(scope.get("headers", []))

        auth_header = headers.get(b'authorization', b'').decode('utf-8')
        print(auth_header)

        if auth_header.startswith('Bearer '):
            return auth_header.split(' ')[1]
        
        else:
            scope['error'] = 'No auth token'
            return None
        
    @database_sync_to_async
    def get_user_from_token(self, token):
            try:
                access_token = AccessToken(token)
                return access_token['user_id']
            except:
                return None

        
from factory.django import DjangoModelFactory
from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
import factory


User = get_user_model()

class UserFactory(DjangoModelFactory):
    class Meta:
        model = User
    first_name = "delight"
    email = "delight@gmail.com"
    image =  factory.LazyAttribute(
            lambda _: ContentFile(
                factory.django.ImageField()._make_data(
                    {'width': 1024, 'height': 768}
                ), 'example.jpg'
            )
        )
    address = 'lagos'
    date_of_birth = "1999-12-20"
    gender = "male"
    bio = "I love eating"
    is_active = False
    password = '123456789'
    username = 'delight'
    
    
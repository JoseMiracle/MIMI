"""
URL configuration for mimi project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),

    path('api/v1/accounts/', include('mimi.accounts.api.v1.urls', namespace='accounts_api_v1')),
    path('api/v1/friendships/', include('mimi.friendships.api.v1.urls', namespace='friendships_api_v1')),
    path('api/v1/posts/', include('mimi.posts.api.v1.urls', namespace='posts_api_v1' )),
    path('api/v1/chats/', include('mimi.chats.api.v1.urls', namespace='chats_api_v1')),
    path('api/v1/currencies/', include('mimi.currencies.api.v1.urls', namespace='currencies_api_v1')),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)





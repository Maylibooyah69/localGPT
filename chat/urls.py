"""URLs for Chat"""

from django.urls import path, include

from rest_framework.routers import DefaultRouter

from chat import views

router = DefaultRouter()
router.register('chats', views.ChatViewSet)

app_name = 'chat'

urlpatterns = [
    path('', include(router.urls)),
]

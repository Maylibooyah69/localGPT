import json
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from yaml import serialize

from core.models import Chat
from chat.serializers import ChatSerializer, ChatDetailSerializer


CHATS_URL = reverse('chat:chat-list')


def detail_url(chat_id):
    """Return chat detail URL."""
    return reverse('chat:chat-detail', args=[chat_id])


def create_chat(user, **params):
    """Create and return a sample chat."""
    defaults = {
        'title': 'Test Chat',
        'summary': 'Test Summary',
        'content': json.dumps({'AI message': 'Hello, World!'}),
    }
    defaults.update(params)

    chat = Chat.objects.create(user=user, **defaults)

    return chat


def create_user(**params):
    """Create and return a sample user."""
    return get_user_model().objects.create_user(**params)


class PublicRecipeAPITests(TestCase):
    """Test the publicly available chat API."""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test that login is required for retrieving chats."""
        res = self.client.get(CHATS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateChatAPITests(TestCase):
    """Test the authorized user chat API."""

    def setUp(self):
        self.client = APIClient()
        self.user = create_user(
            email='user1@example.com', password='testpass123')

        self.client.force_authenticate(self.user)

    def test_retrive_chats(self):
        create_chat(user=self.user)
        create_chat(user=self.user)
        create_chat(user=self.user)

        res = self.client.get(CHATS_URL)

        chats = Chat.objects.all().order_by('-id')
        serializer = ChatSerializer(chats, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_chat_list_limited_to_user(self):
        """Test that chats returned are for the authenticated user."""
        user2 = get_user_model().objects.create_user(
            'user2@example.com',
            'password1234')
        create_chat(user=user2)
        create_chat(user=user2)
        create_chat(user=self.user)

        res = self.client.get(CHATS_URL)

        chats = Chat.objects.filter(user=self.user)
        serializer = ChatSerializer(chats, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_chat_detail(self):
        """Test viewing a chat detail."""
        chat = create_chat(user=self.user)

        url = detail_url(chat.id)
        res = self.client.get(url)

        serializer = ChatDetailSerializer(chat)
        self.assertEqual(res.data, serializer.data)

    def test_create_chat(self):
        """Test creating a chat."""
        payload = {
            'title': 'Test Chat',
            'summary': 'Test Summary',
            'content': json.dumps({}),
        }
        res = self.client.post(CHATS_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        chat = Chat.objects.get(id=res.data['id'])
        for key in payload.keys():
            if key == 'content':
                self.assertEqual(json.loads(payload[key]), getattr(chat, key))
            else:
                self.assertEqual(payload[key], getattr(chat, key))
        self.assertEqual(chat.user, self.user)

    def test_partial_update(self):
        """Test updating a chat with patch."""
        chat = create_chat(user=self.user)
        payload = {
            'title': 'New Title',
        }
        url = detail_url(chat.id)
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        chat.refresh_from_db()
        self.assertEqual(chat.title, payload['title'])
        self.assertEqual(chat.user, self.user)

    def test_update_and_generate(self):
        """Test updating a chat with patch."""
        chat = create_chat(user=self.user)
        with open('chat/liveChatClient/memory.json', 'r') as f:
            data = json.load(f)
        # print(type(data))
        payload = {
            'title': 'New Title',
            'summary': 'New Summary',
            'content': json.dumps(data),
        }

        url = detail_url(chat.id)
        res = self.client.put(url, payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        chat.refresh_from_db()
        self.assertEqual(chat.title, payload['title'])
        self.assertEqual(chat.summary, payload['summary'])
        self.assertEqual(data, chat.content)
        self.assertEqual(chat.user, self.user)

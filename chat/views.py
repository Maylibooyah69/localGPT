"""Views for Chats"""

from rest_framework import viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import Chat
from chat import serializers
from django.shortcuts import render

from rest_framework.generics import CreateAPIView
from .serializers import ChatSerializer

from .liveChatClient.modelIO import load_GPT4all, load_openAI
from .liveChatClient.generate_prompt import default_chat_template
from .liveChatClient.load_chat_content import json_to_memory, memory_to_json, get_last_human_msg_from_mem
from .liveChatClient.generate_chain import generate_chat_chain, call_chain
import json

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from langchain.prompts import PromptTemplate

from langchain.memory import ConversationBufferMemory
from langchain.prompts import (
    ChatPromptTemplate,
    MessagesPlaceholder,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
)
from langchain.schema import messages_from_dict, messages_to_dict
from langchain.memory.chat_message_histories.in_memory import ChatMessageHistory
from langchain.chains import LLMChain
import psutil

template = """You are a chatbot having a conversation with a human.

{chat_history}
Human: {question}
Chatbot:"""

prompt = PromptTemplate(
    input_variables=["chat_history", "question"], template=template
)

# prompt = ChatPromptTemplate(
#     messages=[
#         SystemMessagePromptTemplate.from_template(
#             "You are a nice chatbot having a conversation with a human."
#         ),
#         # The `variable_name` here is what must align with memory
#         MessagesPlaceholder(variable_name="chat_history"),
#         HumanMessagePromptTemplate.from_template("{question}")
#     ]
# )

model = load_GPT4all(
    path='./chat/chatModels/mistral-7b-instruct-v0.1.Q4_0.gguf')
print(model)


class ChatViewSet(viewsets.ModelViewSet):
    """Manage chats Chat APIs"""
    serializer_class = serializers.ChatDetailSerializer
    queryset = Chat.objects.all()
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        """Return objects for the current authenticated user only"""
        return self.queryset.filter(user=self.request.user).order_by('-id')

    def get_serializer_class(self):
        """Return appropriate serializer class"""
        if self.action == 'list':
            return serializers.ChatSerializer
        return super().get_serializer_class()

    def perform_create(self, serializer):
        """Create a new chat"""
        serializer.save(user=self.request.user)

    def perform_update(self, serializer):
        """Update a chat"""
        memory_before = psutil.Process().memory_info().rss
        data = serializer.validated_data
        memory = json_to_memory(data['content'])
        # memory = ConversationBufferMemory(
        #     memory_key="chat_history", return_messages=True)
        conversation = LLMChain(
            llm=model,
            prompt=prompt,
            verbose=True,
            memory=memory
        )
        last_human_msg = get_last_human_msg_from_mem(memory)
        response = conversation(
            {"question": last_human_msg},)
        data['content'] = memory_to_json(memory)
        # print(response.content, type(json.loads(data['content'])))
        serializer.save(user=self.request.user,)
        # Get the memory usage after the operation
        memory_after = psutil.Process().memory_info().rss

        # Print the memory usage
        print(f'Memory usage before: {memory_before / 1024 / 1024} MB')
        print(f'Memory usage after: {memory_after / 1024 / 1024} MB')
        print(
            f'Memory used: {(memory_after - memory_before) / 1024 / 1024} MB')


def simple_chat_view(request):
    return render(request, 'chat/simple_chat.html', {})



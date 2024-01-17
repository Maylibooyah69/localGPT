from django.contrib.auth.hashers import make_password
from django.contrib.auth import get_user_model
from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ['email', 'password', 'username']
        extra_kwargs = {
            'password': {
                'write_only': True,
                'min_length': 8,
            }
        }

    def create(self, validated_data):
        password = make_password(validated_data['password'])
        user = get_user_model().objects.create(
            email=validated_data['email'],
            password=password,
            username=validated_data['username']
        )
        return user

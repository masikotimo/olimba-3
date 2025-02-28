from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Achievement

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password']
        extra_kwargs = {'password': {'write_only': True}}
        read_only_fields = ['date_joined']

    def create(self, validated_data):
        user = User(**validated_data)
        user.set_password(validated_data['password'])  # Hash the password
        user.save()
        return user

class AchievementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Achievement
        fields = ['id', 'title', 'description', 'unlocked_at']
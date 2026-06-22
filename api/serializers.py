from rest_framework import serializers
from django.contrib.auth import get_user_model
from accounts.models import User

# User Serializer
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 
                 'role', 'phone_number', 'employee_id', 'is_active')
        read_only_fields = ('id', 'created_at', 'updated_at')

# User Create Serializer
class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password', 'first_name', 
                 'last_name', 'role', 'phone_number', 'employee_id')
    
    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User.objects.create_user(**validated_data)
        user.set_password(password)
        user.save()
        return user

# Login Serializer
class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()
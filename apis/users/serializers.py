from rest_framework import serializers
from .models import User, Profile
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)

        # Add custom claims to the token
        data['user'] = {
            "id": self.user.id,
            "username": self.user.username,
            "email": self.user.email,
            "role": self.user.role,  # Assuming role is a field on your User model
        }

        return data

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Add custom claims to the token itself
        token['username'] = user.username
        token['role'] = user.role  # Add role to the token claims

        return token


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ['phone_number', 'address', 'avatar']  # Profile-specific fields


class UserSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer(read_only=True)  # Include profile as a nested serializer

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'role', 'is_locked', 'profile']  # User fields + profile
        read_only_fields = ['id']


class UserCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating a new user with a profile.
    """
    # Optional fields for the profile
    phone_number = serializers.CharField(required=False, allow_blank=True)
    address = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'role', 'is_locked', 'phone_number', 'address']
        extra_kwargs = {
            'password': {'write_only': True},  # Hide password in responses
        }

    def create(self, validated_data):
        # Extract profile fields from validated data
        profile_data = {
            'phone_number': validated_data.pop('phone_number', None),
            'address': validated_data.pop('address', None),
        }

        # Create user instance
        user = User.objects.create_user(**validated_data)

        # Create associated profile if any profile fields are provided
        if profile_data:
            Profile.objects.create(user=user, **profile_data)

        return user
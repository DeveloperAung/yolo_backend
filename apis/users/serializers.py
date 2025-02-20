from django.contrib.auth import get_user_model, authenticate
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken

from .models import User, Profile
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth.password_validation import validate_password


User = get_user_model()


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)

        # Add custom claims to the token
        data['user'] = {
            "id": self.user.id,
            "username": self.user.username,
            "email": self.user.email,
            "phone_number": self.user.phone_number,
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
        fields = ['id', 'username', 'email', 'phone_number', 'role', 'avatar',
                  'is_locked', 'profile', 'created_on', 'modified_on']
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
        fields = ['username', 'email', 'avatar', 'phone_number', 'password', 'role', 'is_locked', 'phone_number', 'address']
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


class UserRegisterSerializer(serializers.ModelSerializer):
    confirm_password = serializers.CharField(write_only=True)
    phone_number = serializers.CharField(write_only=True, required=False, allow_blank=True)
    address = serializers.CharField(write_only=True, required=False, allow_blank=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'confirm_password', 'role', 'phone_number', 'address']
        extra_kwargs = {'password': {'write_only': True}}

    def validate(self, data):
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError({"password": "Passwords do not match"})
        return data

    def create(self, validated_data):
        phone_number = validated_data.pop('phone_number', None)
        address = validated_data.pop('address', None)

        validated_data.pop('confirm_password')  # Remove confirm_password from data
        user = User.objects.create_user(**validated_data)  # Create user

        # Create profile only if phone_number or address is provided
        Profile.objects.create(
            user=user,
            phone_number=phone_number if phone_number else None,
            address=address if address else None
        )

        return user


class AdminUserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)
    confirm_password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'phone_number', 'avatar', 'role', 'password', 'confirm_password']

    def validate(self, data):
        # Check if passwords match
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError({"confirm_password": "Passwords do not match"})

        validate_password(data['password'])  # Validate password strength
        return data

    def create(self, validated_data):
        validated_data.pop('confirm_password')  # Remove confirm_password before saving
        user = User.objects.create_user(**validated_data)
        return user


class UserLoginSerializer(serializers.Serializer):
    # id = serializers.IntegerField()
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)
    role = serializers.CharField(read_only=True)
    access = serializers.CharField(read_only=True)
    refresh = serializers.CharField(read_only=True)
    avatar = serializers.SerializerMethodField()  # ✅ Explicitly add avatar field

    def get_avatar(self, obj):
        """Returns the full avatar URL if available, otherwise None"""
        user = self.context.get("user")  # ✅ Get user instance from context
        if user and user.avatar:  # Ensure avatar exists
            request = self.context.get("request")  # Get request context for absolute URL
            return request.build_absolute_uri(user.avatar.url) if request else user.avatar.url
        return None  # Return None if no avatar is set


    def validate(self, data):
        username = data.get("username")
        password = data.get("password")
        user = authenticate(username=username, password=password)

        if user is None:
            # print("Invalid username or password")
            raise serializers.ValidationError("Invalid username or password")

        if user.is_locked:
            raise serializers.ValidationError("Your account is locked. Contact admin.")

        refresh = RefreshToken.for_user(user)

        self.context["user"] = user

        return {
            "id": user.id,
            "username": user.username,
            "role": user.role,
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "avatar": self.get_avatar(user),
        }


class PasswordChangeSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True, required=True)
    new_password = serializers.CharField(write_only=True, required=True)
    confirm_new_password = serializers.CharField(write_only=True, required=True)

    def validate_new_password(self, value):
        validate_password(value)  # Ensures password meets Django's security rules
        return value

    def validate(self, data):
        user = self.context['request'].user

        # Check if old password is correct
        if not user.check_password(data['old_password']):
            raise serializers.ValidationError({"old_password": "Old password is incorrect"})

        # Check if new password and confirm password match
        if data['new_password'] != data['confirm_new_password']:
            raise serializers.ValidationError({"confirm_new_password": "Passwords do not match"})

        return data

    def update(self, instance, validated_data):
        instance.set_password(validated_data['new_password'])
        instance.save()
        return instance

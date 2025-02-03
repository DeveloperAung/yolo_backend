from rest_framework import serializers
from .models import Cart, CartItem
from ..courses.serializers import CourseSerializer
from ..users.models import User
from ..users.serializers import UserSerializer


class CartSerializer(serializers.ModelSerializer):
    cart_username = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = ['id', 'user']

    def get_cart_user(self, obj):
        return obj.user.username if obj.user else None


class CartItemSerializer(serializers.ModelSerializer):
    course = CourseSerializer(many=True, read_only=True)  # Nested serializer for lessons
    cart = CartSerializer(many=True, read_only=True)
    cart_username = serializers.SerializerMethodField()

    class Meta:
        model = CartItem
        fields = [
            'id', 'cart', 'course', 'price'
        ]

    def get_cart_user(self, obj):
        return obj.instructor.username if obj.instructor else None

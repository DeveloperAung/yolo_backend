from rest_framework import serializers
from .models import Cart, CartItem
from ..courses.serializers import CourseCreateSerializer
from ..courses.models import Course
from ..users.models import User
from ..users.serializers import UserSerializer


# class CartSerializer(serializers.ModelSerializer):
#     cart_username = serializers.SerializerMethodField()
#
#     class Meta:
#         model = Cart
#         fields = ['id', 'user']
#
#     def get_cart_user(self, obj):
#         return obj.user.username if obj.user else None


class CartItemSerializer(serializers.ModelSerializer):
    course = CourseCreateSerializer(read_only=True)  # Nested serializer for lessons
    # cart = CartSerializer(many=True, read_only=True)
    # cart_username = serializers.SerializerMethodField()

    class Meta:
        model = CartItem
        fields = [
            'id', 'course', 'price'
        ]

    # def get_cart_user(self, obj):
    #     return obj.instructor.username if obj.instructor else None


class AddToCartSerializer(serializers.Serializer):
    course_id = serializers.IntegerField()
    price = serializers.DecimalField(max_digits=10, decimal_places=2)

    def validate_course_id(self, value):
        if not Course.objects.filter(id=value).exists():
            raise serializers.ValidationError("Course does not exist.")
        return value

    def create(self, validated_data):
        user = self.context['request'].user
        course_id = validated_data.get('course_id')
        price = validated_data.get('price')

        # Create cart on demand
        cart, _ = Cart.objects.get_or_create(user=user)

        # Check if course is already in the cart
        if CartItem.objects.filter(cart=cart, course_id=course_id).exists():
            raise serializers.ValidationError("Course is already in the cart.")

        # Add course to cart
        cart_item = CartItem.objects.create(cart=cart, course_id=course_id, price=price)
        return cart_item

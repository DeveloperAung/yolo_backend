from rest_framework import serializers
from .models import Course, Lesson
from ..cart.models import Cart
from ..core.middleware import get_current_user
from ..orders.models import Order, OrderItem
from ..users.models import User
from ..users.serializers import UserSerializer


class LessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = [
            'id', 'title', 'content', 'video', 'duration', 'is_demo', 'course', 'order'
        ]


class CourseListSerializer(serializers.ModelSerializer):
    instructor_username = serializers.SerializerMethodField()
    lessons = LessonSerializer(many=True, read_only=True)
    in_cart = serializers.SerializerMethodField()
    is_purchased = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = [
            'id', 'title', 'recommendation', 'total_duration', 'description', 'created_on', 'modified_on', 'instructor',
            'instructor_username', 'cover_image', 'demo_video', 'is_published', 'lessons', 'is_on_sale',
            'price', 'sale_price', 'in_cart', 'is_purchased'
        ]

    current_user = get_current_user()

    def get_instructor_username(self, obj):
        return obj.instructor.username if obj.instructor else None

    def get_in_cart(self, obj):
        try:
            request = self.context.get('request')
            if request and hasattr(request, "user") and request.user.is_authenticated:
                return Cart.objects.filter(user=request.user, cart_item__course=obj).exists()
            return False  # Default to False for unauthenticated users
        except Exception as e:
            print('Error in get_in_cart:', e)
            return False

    def get_is_purchased(self, obj):
        request = self.context.get('request')
        if request and hasattr(request, "user") and request.user.is_authenticated:
            items = OrderItem.objects.filter(order__user=request.user, course=obj, order__status='accepted')
            return items.exists()
        return False


class CourseCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = [
            'title', 'recommendation', 'description', 'cover_image', 'demo_video', 'is_on_sale', 'price', 'sale_price'
        ]


class CourseDeleteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ['is_active']

# class CourseSerializer(serializers.ModelSerializer):
#     lessons = LessonSerializer(many=True, read_only=True)  # Nested serializer for lessons
#     instructor_username = serializers.SerializerMethodField()
#
#     class Meta:
#         model = Course
#         fields = [
#             'id', 'title', 'recommendation', 'total_duration', 'description', 'created_on', 'modified_on'
#             'instructor', 'instructor_username', 'cover_image', 'demo_video', 'is_published', 'lessons', 'is_on_sale',
#             'price', 'sale_price'
#         ]
#
#     def get_instructor_username(self, obj):
#         return obj.instructor.username if obj.instructor else None

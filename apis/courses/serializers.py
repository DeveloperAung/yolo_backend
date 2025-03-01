from rest_framework import serializers
from .models import Course, Lesson
from ..cart.models import Cart
from ..core.middleware import get_current_user
from ..orders.models import Order, OrderItem
from ..users.models import User
from ..users.serializers import UserSerializer


class LessonSerializer(serializers.ModelSerializer):
    video = serializers.SerializerMethodField()
    course_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Lesson
        fields = [
            'id', 'title', 'content', 'video', 'duration', 'is_demo', 'course', 'course_id', 'order'
        ]
        read_only_fields = ['course']

    def get_video(self, obj):
        request = self.context.get('request')
        if obj.video:
            relative_url = obj.video.url  # This is usually a relative URL
            if request:
                return request.build_absolute_uri(relative_url)
            return relative_url
        return ''

    def validate(self, data):
        if 'title' in data and len(data['title']) < 3:
            raise serializers.ValidationError({"title": "Title must be at least 3 characters long."})
        return data

    def create(self, validated_data):
        try:
            return super().create(validated_data)
        except Exception as e:
            raise serializers.ValidationError({"error": str(e)})

    def update(self, instance, validated_data):
        try:
            return super().update(instance, validated_data)
        except Exception as e:
            raise serializers.ValidationError({"error": str(e)})


class LessonDeleteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = ['is_active']


class CourseListSerializer(serializers.ModelSerializer):
    instructor_username = serializers.SerializerMethodField()
    lessons = serializers.SerializerMethodField()
    in_cart = serializers.SerializerMethodField()
    is_purchased = serializers.SerializerMethodField()
    is_ordered = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = [
            'id', 'title', 'recommendation', 'total_duration', 'description', 'created_on', 'modified_on', 'instructor',
            'instructor_username', 'cover_image', 'demo_video', 'is_published', 'lessons', 'is_on_sale',
            'price', 'sale_price', 'in_cart', 'is_purchased', 'is_ordered'
        ]

    current_user = get_current_user()

    def get_lessons(self, obj):
        # Get only active lessons (is_active=True)
        active_lessons = obj.lessons.filter(is_active=True)
        return LessonSerializer(active_lessons, many=True, context=self.context).data

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

    def get_is_ordered(self, obj):
        request = self.context.get('request')
        if request and hasattr(request, "user") and request.user.is_authenticated:
            items = OrderItem.objects.filter(order__user=request.user, course=obj)
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

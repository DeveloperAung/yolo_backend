from rest_framework import serializers
from .models import Course, Lesson
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

    class Meta:
        model = Course
        fields = [
            'id', 'title', 'recommendation', 'total_duration', 'description', 'created_on', 'modified_on', 'instructor',
            'instructor_username', 'cover_image', 'demo_video', 'is_published', 'lessons', 'is_on_sale',
            'price', 'sale_price'
        ]

    def get_instructor_username(self, obj):
        return obj.instructor.username if obj.instructor else None


class CourseCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = [
            'title', 'recommendation', 'description', 'cover_image', 'demo_video', 'is_on_sale', 'price', 'sale_price'
        ]


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

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


class CourseSerializer(serializers.ModelSerializer):
    lessons = LessonSerializer(many=True, read_only=True)  # Nested serializer for lessons
    instructor_username = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = [
            'id', 'title', 'recommendation', 'total_duration', 'description',
            'instructor', 'instructor_username', 'cover_image', 'demo_video', 'is_published', 'lessons'
        ]

    def get_instructor_username(self, obj):
        return obj.instructor.username if obj.instructor else None

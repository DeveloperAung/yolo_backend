import logging

from rest_framework import generics, permissions, status
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response

from .models import Course, Lesson
from .serializers import CourseSerializer, LessonSerializer
from apis.users.permissions import IsAdminOrInstructor
from ..core.utlis import api_response

logger = logging.getLogger(__name__)


class CourseListCreateView(generics.ListCreateAPIView):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminOrInstructor]  # Require authentication

    def list(self, request, *args, **kwargs):
        try:
            queryset = self.get_queryset()
            serializer = self.get_serializer(queryset, many=True)
            return api_response(
                status="success",
                message="Courses retrieved successfully.",
                data=serializer.data,
                http_status=status.HTTP_200_OK,
            )
        except Exception as e:
            return api_response(
                status="error",
                message="An unexpected error occurred while retrieving courses.",
                errors={"detail": str(e)},
                http_status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def create(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            return api_response(
                status="success",
                message="Course created successfully.",
                data=serializer.data,
                http_status=status.HTTP_201_CREATED,
            )
        except Exception as e:
            return api_response(
                status="error",
                message="Course creation failed.",
                errors=serializer.errors if hasattr(serializer, 'errors') else {"detail": str(e)},
                http_status=status.HTTP_400_BAD_REQUEST,
            )


class CourseUpdateView(generics.UpdateAPIView):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    # permission_classes = [permissions.IsAuthenticated, IsAdminOrInstructor]
    parser_classes = [MultiPartParser, FormParser]  # Enable file upload parsing

    def update(self, request, *args, **kwargs):
        try:
            # Log the incoming request
            logger.info(f"Updating course with ID {kwargs.get('pk')} by user {request.user}")

            # Call the parent update method
            response = super().update(request, *args, **kwargs)

            # Log the successful update
            logger.info(f"Course with ID {kwargs.get('pk')} updated successfully")
            return Response({
                "status": "success",
                "message": "Course updated successfully.",
                "data": response.data,
            }, status=status.HTTP_200_OK)

        except Exception as e:
            # Log the exception
            logger.error(f"Error updating course with ID {kwargs.get('pk')}: {str(e)}")
            print('error', e)
            # Return a structured error response
            return Response({
                "status": "error",
                "message": "An error occurred while updating the course.",
                "errors": {"detail": str(e)},
            }, status=status.HTTP_400_BAD_REQUEST)


class CourseDetailView(generics.RetrieveUpdateAPIView):
    """
    API to retrieve, update, or delete a course.
    """
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminOrInstructor]  # Add custom permissions if needed


class LessonListCreateView(generics.ListCreateAPIView):
    """
    API to list all lessons for a course and create a new lesson.
    """
    serializer_class = LessonSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminOrInstructor]

    def get_queryset(self):
        course_id = self.kwargs['course_id']
        return Lesson.objects.filter(course__id=course_id)

    def perform_create(self, serializer):
        course_id = self.kwargs['course_id']
        course = Course.objects.get(id=course_id)
        serializer.save(course=course)


class LessonDetailView(generics.RetrieveUpdateAPIView):
    """
    API to retrieve, update, or delete a lesson.
    """
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminOrInstructor]

from django.urls import path
from .views import CourseListCreateView, CourseDetailView, LessonListCreateView, LessonDetailView, CourseUpdateView

urlpatterns = [
    # Course endpoints
    path('', CourseListCreateView.as_view(), name='course_list_create'),
    path('update/<int:pk>/', CourseUpdateView.as_view(), name='course_update'),
    path('details/<int:pk>/', CourseDetailView.as_view(), name='course_details'),

    # Lesson endpoints
    path('<int:course_id>/lessons/', LessonListCreateView.as_view(), name='lesson_list_create'),
    path('lessons/<int:pk>/', LessonDetailView.as_view(), name='lesson_detail'),
]

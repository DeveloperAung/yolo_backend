from django.urls import path
from .views import CourseDetailView, LessonListCreateView, LessonDetailView, CourseUpdateView, \
    CourseListAPIView, CourseCreateAPIView, CourseDeleteView

urlpatterns = [
    # Course endpoints
    # path('', CourseListCreateView.as_view(), name='course_list_create'),
    path('', CourseListAPIView.as_view(), name='course_list'),
    path('create/', CourseCreateAPIView.as_view(), name='course_create'),
    path('update/<int:pk>/', CourseUpdateView.as_view(), name='course_update'),
    path('delete/<int:pk>/', CourseDeleteView.as_view(), name='course_delete'),
    path('details/<int:pk>/', CourseDetailView.as_view(), name='course_details'),

    # Lesson endpoints
    path('<int:course_id>/lessons/', LessonListCreateView.as_view(), name='lesson_list_create'),
    path('lessons/<int:pk>/', LessonDetailView.as_view(), name='lesson_detail'),
]

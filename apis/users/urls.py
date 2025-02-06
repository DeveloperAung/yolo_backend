from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from .views import *

urlpatterns = [
    path('login/', LoginAPIView.as_view(), name='login'),
    path('password/change/', PasswordChangeAPIView.as_view(), name='password-change'),

    path('token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('logout/', LogoutView.as_view(), name='logout'),

    # path('list/', UserListView.as_view(), name='user_list'),
    path('list/', UserListAPIView.as_view(), name='user-list'),
    path('<int:pk>/', UserDetailView.as_view(), name='user_detail'),
    path('register/', RegisterAPIView.as_view(), name='user_register'),
    path('admin/create-user/', AdminCreateUserAPIView.as_view(), name='admin-create-user'),
    path('create/', UserCreateView.as_view(), name='user_create'),
    path('update/<int:pk>/', UserUpdateView.as_view(), name='user_update'),

    path('instructors/', InstructorListView.as_view(), name='instructor_list'),
]

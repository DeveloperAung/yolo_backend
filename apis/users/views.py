from rest_framework.exceptions import NotFound
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.views import APIView
from rest_framework import status
from django.contrib.auth import authenticate, get_user_model
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.views import TokenObtainPairView

from .permissions import IsAdminUserOnly, IsAdminOrInstructor
from .serializers import UserSerializer, UserCreateSerializer, CustomTokenObtainPairSerializer, UserRegisterSerializer, \
    UserLoginSerializer, PasswordChangeSerializer, AdminUserCreateSerializer
import logging

from apis.core.utlis import api_response

logger = logging.getLogger(__name__)

User = get_user_model()


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


class LoginView(APIView):
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        if not username or not password:
            logger.error("Username or password missing.")
            return api_response(
                status="error",
                message="Username and password are required.",
                http_status=status.HTTP_400_BAD_REQUEST,
            )

        user = authenticate(username=username, password=password)

        if not user:
            logger.warning(f"Authentication failed for username: {username}")
            return api_response(
                status="error",

                http_status=status.HTTP_401_UNAUTHORIZED,
            )

        refresh = RefreshToken.for_user(user)

        user_data = {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "role": user.role,  # Assuming `role` is a field on your User model
        }
        logger.info(f"User {username} logged in successfully.")

        return api_response(
            status="success",
            message="Login successful.",
            data={
                "refresh": str(refresh),
                "access": str(refresh.access_token),
                "user_data": user_data,
            },
            http_status=status.HTTP_200_OK,
        )


class LogoutView(APIView):
    def post(self, request):
        refresh_token = request.data.get("refresh")

        if not refresh_token:
            logger.error("Refresh token missing in logout request.")
            return api_response(
                status="error",
                message="Refresh token is required.",
                http_status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
            logger.info("User successfully logged out.")
            return api_response(
                status="success",
                message="Logout successful.",
                http_status=status.HTTP_200_OK,
            )
        except Exception as e:
            logger.exception("An unexpected error occurred during logout.")
            return api_response(
                status="error",
                message="An unexpected error occurred.",
                errors={"details": str(e)},
                http_status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class UserListView(ListAPIView):
    """
    Retrieve a list of all users.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def list(self, request, *args, **kwargs):
        try:
            # Fetch all users
            logger.info("Fetching the list of all users.")
            queryset = self.get_queryset()
            serializer = self.get_serializer(queryset, many=True)
            return Response({
                "status": "success",
                "message": "User list retrieved successfully.",
                "data": serializer.data,
            }, status=status.HTTP_200_OK)
        except Exception as e:
            logger.exception("An unexpected error occurred in UserListView.", e)
            return Response({
                "status": "error",
                "message": "An unexpected error occurred.",
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UserListAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            users = User.objects.all().values("id", "username", "email", "role")
            user_list = list(users)

            return Response(
                {
                    "status": "success",
                    "message": "User list retrieved successfully",
                    "data": user_list
                },
                status=status.HTTP_200_OK
            )
        except Exception as e:
            logger.exception("An unexpected error occurred in UserListView.", e)
            return Response({
                "status": "error",
                "message": "An unexpected error occurred.",
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UserDetailView(RetrieveAPIView):
    """
    Retrieve a single user's details.
    """
    queryset = User.objects.all()
    # permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer
    #
    # def get_object(self):
    #     return self.request.user

    def retrieve(self, request, *args, **kwargs):
        try:

            # Retrieve the specific user
            instance = self.get_object()
            print('start ', instance)
            logger.info(f"Retrieving details for user: {instance.username}")
            serializer = self.get_serializer(instance)
            return Response({
                "status": "success",
                "message": "User retrieved successfully.",
                "data": serializer.data,
            }, status=status.HTTP_200_OK)
        except NotFound as e:
            logger.error(f"User not found. Detail: {str(e)}")
            print('user not found')
            return Response({
                "status": "error",
                "message": "User not found.",
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.exception("An unexpected error occurred in UserDetailView.", e)
            return Response({
                "status": "error",
                "message": "An unexpected error occurred.",
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class RegisterAPIView(APIView):
    def post(self, request):
        serializer = UserRegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    "status": "success",
                    "message": "User registered successfully",
                    "data": serializer.data,
                },
                status=status.HTTP_201_CREATED,
            )
        return Response(
            {
                "status": "error",
                "message": "Registration failed",
                "errors": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )


class LoginAPIView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):
        print('inside post', request.data)
        serializer = UserLoginSerializer(data=request.data)
        print('request data', request.data)
        if serializer.is_valid():

            return Response(
                {
                    "status": "success",
                    "message": "Login successful",
                    "data": {
                        "id": serializer.validated_data["id"],
                        "username": serializer.validated_data["username"],
                        "role": serializer.validated_data["role"],
                        "access_token": serializer.validated_data["access"],
                        "refresh_token": serializer.validated_data["refresh"],
                    },
                },
                status=status.HTTP_200_OK,
            )
        return Response(
            {
                "status": "error",
                "message": "Invalid credentials",
                "errors": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )


class UserCreateView(APIView):
    """
    API to create a new user. Only accessible by admins.
    """
    permission_classes = [IsAuthenticated]  # Ensure user is authenticated

    def post(self, request):
        # Check if the requesting user is an admin
        if not request.user.is_staff:
            logger.warning(f"Unauthorized user creation attempt by {request.user.username}")
            return Response({
                "status": "error",
                "message": "You do not have permission to perform this action."
            }, status=status.HTTP_403_FORBIDDEN)

        # Validate and create the user
        serializer = UserCreateSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            logger.info(f"New user created: {user.username} by admin {request.user.username}")
            return Response({
                "status": "success",
                "message": "User created successfully.",
                "data": {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                    "role": 'student',
                }
            }, status=status.HTTP_201_CREATED)
        else:
            logger.error("User creation failed due to validation errors.")
            return Response({
                "status": "error",
                "message": "Failed to create user.",
                "errors": serializer.errors,
            }, status=status.HTTP_400_BAD_REQUEST)


class UserUpdateView(APIView):
    """
    API to update user details.
    Only accessible by authenticated users.
    """
    permission_classes = [IsAuthenticated]

    def put(self, request, pk):
        try:
            # Fetch the user to be updated
            user = User.objects.get(pk=pk)
        except User.DoesNotExist:
            return Response({
                "status": "error",
                "message": "User not found."
            }, status=status.HTTP_404_NOT_FOUND)

        # Serialize and validate incoming data
        serializer = UserSerializer(user, data=request.data, partial=True)  # Use `partial=True` for partial updates
        if serializer.is_valid():
            serializer.save()  # Save the updates
            return Response({
                "status": "success",
                "message": "User updated successfully.",
                "data": serializer.data
            }, status=status.HTTP_200_OK)

        return Response({
            "status": "error",
            "message": "Failed to update user.",
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


class PasswordChangeAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = PasswordChangeSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            user = request.user
            user.set_password(serializer.validated_data['new_password'])  # Update password manually
            user.save()

            return Response(
                {
                    "status": "success",
                    "message": "Password changed successfully",
                    "data": None
                },
                status=status.HTTP_200_OK
            )
        return Response(
            {
                "status": "error",
                "message": "Password change failed",
                "errors": serializer.errors
            },
            status=status.HTTP_400_BAD_REQUEST
        )


class AdminCreateUserAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # Ensure only admins can create users
        if request.user.role != "admin":
            return Response(
                {"status": "error", "message": "Only admins can create users"},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = AdminUserCreateSerializer(data=request.data)
        print('user data', request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response(
                {
                    "status": "success",
                    "message": "User created successfully",
                    "data": {
                        "id": user.id,
                        "username": user.username,
                        "email": user.email,
                        "role": user.role,
                        # "image": user.image
                    }
                },
                status=status.HTTP_201_CREATED
            )

        print('error', serializer.errors)
        return Response(
            {
                "status": "error",
                "message": "User creation failed",
                "errors": serializer.errors
            },
            status=status.HTTP_400_BAD_REQUEST
        )


class InstructorListView(APIView):
    """
    API to retrieve a list of instructors.
    """
    permission_classes = [IsAuthenticated, IsAdminOrInstructor]

    def get(self, request):
        try:
            # Fetch users with the 'instructor' role
            instructors = User.objects.filter(role='instructor')

            if not instructors.exists():
                logger.warning("No instructors found.")
                return api_response(
                    status="error",
                    message="No instructors found.",
                    http_status=status.HTTP_404_NOT_FOUND,
                )

            serializer = UserSerializer(instructors, many=True)
            return api_response(
                status="success",
                message="Instructors retrieved successfully.",
                data=serializer.data,
                http_status=status.HTTP_200_OK,
            )

        except Exception as e:
            logger.error(f"Error retrieving instructors: {str(e)}")
            return api_response(
                status="error",
                message="An unexpected error occurred while retrieving instructors.",
                errors={"detail": str(e)},
                http_status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

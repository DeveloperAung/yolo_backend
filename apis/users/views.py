from google.auth.transport import requests
from google.oauth2 import id_token
from rest_framework.exceptions import NotFound
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.views import APIView
from rest_framework import status
from django.contrib.auth import authenticate, get_user_model
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.views import TokenObtainPairView
from django.db.models import F
from django.conf import settings
from django.core.mail import send_mail
from django.utils.crypto import get_random_string
from .models import PasswordReset
from .permissions import IsAdminUserOnly, IsAdminOrInstructor
from .serializers import UserSerializer, UserCreateSerializer, CustomTokenObtainPairSerializer, UserRegisterSerializer, \
    UserLoginSerializer, PasswordChangeSerializer, AdminUserCreateSerializer, ResetPasswordSerializer, \
    ForgotPasswordSerializer
import logging
from PIL import Image
import io
from django.core.files.uploadedfile import InMemoryUploadedFile

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
            "contact": user.contact,
            "role": user.role,  # Assuming `role` is a field on your User model
            "avatar": request.build_absolute_uri(user.avatar.url) if user.avatar else None,
            "created_on": user.created_on,
            "modified_on": user.modified_on,
        }
        logger.info(f"User {username} logged in successfully.")
        # print('avatar url', user_data['avatar'])
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
            users = User.objects.all().annotate(
                avatar_url=F("avatar")  # Use F() to ensure we get the field value
            ).values("id", "username", "email", "phone_number", "role", "avatar")
            user_list = list(users)

            for user in user_list:
                if user["avatar"]:
                    user["avatar"] = request.build_absolute_uri(settings.MEDIA_URL + user["avatar"])

            # print('user_list', user_list)
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
            print('exception', e)
            logger.exception("An unexpected error occurred in UserDetailView.", e)
            return Response({
                "status": "error",
                "message": "An unexpected error occurred.",
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class RegisterAPIView(APIView):
    permission_classes = [AllowAny]

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
        # print('inside post', request.data)
        serializer = UserLoginSerializer(data=request.data, context={"request": request})
        # print('request data', request.data)
        if serializer.is_valid():
            print('serializer data', serializer.data)
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
                        "avatar": serializer.get_avatar(serializer.validated_data["avatar"]),
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
            user = User.objects.get(pk=pk)
        except User.DoesNotExist:
            return Response({"status": "error", "message": "User not found."}, status=status.HTTP_404_NOT_FOUND)

        # Merge request.data and request.FILES for file handling
        # data = request.data.copy()
        if "avatar" in request.FILES:
            avatar_file = request.FILES["avatar"]
            if avatar_file.size > 5 * 1024 * 1024:  # If file size > 5MB
                avatar_file = self._resize_image(avatar_file)
            request.FILES["avatar"] = avatar_file  # Replace with compressed image

        serializer = UserSerializer(user, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response({"status": "success", "message": "User updated successfully.", "data": serializer.data},
                            status=status.HTTP_200_OK)
        print('is not valid', serializer.errors)
        return Response({"status": "error", "message": "Failed to update user.", "errors": serializer.errors},
                        status=status.HTTP_400_BAD_REQUEST)

    def _resize_image(self, image_file):
        """Resizes image to reduce file size if larger than 5MB."""
        image = Image.open(image_file)
        image = image.convert("RGB")  # Ensure it's in RGB mode

        # Reduce quality & resize while maintaining aspect ratio
        max_size = (1024, 1024)  # Resize to max 1024x1024 pixels
        image.thumbnail(max_size)

        # Save resized image into a memory buffer
        buffer = io.BytesIO()
        image.save(buffer, format="JPEG", quality=75)  # Reduce quality to 75%
        buffer.seek(0)

        # Create a new InMemoryUploadedFile
        new_image = InMemoryUploadedFile(
            buffer, "ImageField", image_file.name, "image/jpeg", buffer.getbuffer().nbytes, None
        )
        return new_image


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


class ForgotPasswordView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = ForgotPasswordSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                return Response({"detail": "User not found"}, status=status.HTTP_404_NOT_FOUND)

            # Generate a 6-digit numeric PIN
            pin = get_random_string(length=6, allowed_chars='0123456789')
            # print('generated pin', pin)
            # Save the PIN in our PasswordReset model
            PasswordReset.objects.create(user=user, pin=pin)
            # print('created_password-reset', settings.EMAIL_HOST_USER)
            # Send the PIN to the user's email
            send_mail(
                'Password Reset PIN',
                f'Your password reset PIN is {pin}',
                settings.EMAIL_HOST_USER,  # Replace with your sender email
                [email],
                fail_silently=False,
            )
            # print('email send completed')
            return Response({"detail": "PIN sent to email"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ResetPasswordView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = ResetPasswordSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            pin = serializer.validated_data['pin']
            new_password = serializer.validated_data['new_password']

            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                return Response({"detail": "User not found"}, status=status.HTTP_404_NOT_FOUND)

            # Find the latest unused PIN for the user
            try:
                reset_instance = PasswordReset.objects.filter(user=user, pin=pin, is_used=False).latest('created_at')
            except PasswordReset.DoesNotExist:
                return Response({"detail": "Invalid PIN"}, status=status.HTTP_400_BAD_REQUEST)

            if not reset_instance.is_valid():
                return Response({"detail": "PIN expired or already used"}, status=status.HTTP_400_BAD_REQUEST)

            # Set the new password
            user.set_password(new_password)
            user.save()

            # Mark the PIN as used
            reset_instance.is_used = True
            reset_instance.save()

            return Response({"detail": "Password reset successful"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


GOOGLE_CLIENT_ID = "230980647742-6v9bp4ovcp0s0bkqgnstgrl4o8juhgbe.apps.googleusercontent.com"


# class GoogleAuthAPIView(APIView):
#     permission_classes = [AllowAny]
#
#     def post(self, request, *args, **kwargs):
#         token = request.data.get('id_token')
#         if not token:
#             return Response({"error": "No token provided."}, status=status.HTTP_400_BAD_REQUEST)
#
#         try:
#             # Verify Google ID token
#             idinfo = id_token.verify_oauth2_token(token, requests.Request(), GOOGLE_CLIENT_ID)
#
#             email = idinfo.get('email')
#             name = idinfo.get('name')
#             avatar = idinfo.get('picture')
#
#             # Check if user exists, otherwise create one
#             user, created = User.objects.get_or_create(email=email,
#                                                        defaults={"username": email.split("@")[0], "fullname": name})
#
#             # Generate JWT tokens
#             refresh = RefreshToken.for_user(user)
#             access = refresh.access_token
#
#             return Response({
#                 "status": "success",
#                 "message": "Login successful",
#                 "data": {
#                     "id": user.id,
#                     "username": user.username,
#                     "role": user.role if hasattr(user, 'role') else "user",
#                     "access_token": str(access),
#                     "refresh_token": str(refresh),
#                     "avatar": avatar,
#                 },
#             }, status=status.HTTP_200_OK)
#
#         except ValueError as exc:
#             return Response({"error": str(exc)}, status=status.HTTP_400_BAD_REQUEST)


class GoogleAuthAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        token = request.data.get('id_token')
        if not token:
            return Response({"status": "error", "message": "No token provided."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Verify Google ID token
            idinfo = id_token.verify_oauth2_token(token, requests.Request(), GOOGLE_CLIENT_ID)

            email = idinfo.get('email')
            name = idinfo.get('name')
            avatar = idinfo.get('picture')

            # ✅ Check if user exists, otherwise create one
            user, created = User.objects.get_or_create(
                email=email,
                defaults={"username": email.split("@")[0], "fullname": name}
            )

            # ✅ Generate JWT tokens
            refresh = RefreshToken.for_user(user)
            access = refresh.access_token

            return Response({
                "status": "success",
                "message": "Login successful",
                "data": {
                    "id": user.id,
                    "username": user.username,
                    "role": user.role if hasattr(user, 'role') else "user",
                    "access_token": str(access),
                    "refresh_token": str(refresh),
                    "avatar": avatar,
                },
            }, status=status.HTTP_200_OK)

        except ValueError as exc:
            return Response({"status": "error", "message": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        
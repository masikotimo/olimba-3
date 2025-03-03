from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth import get_user_model, authenticate, login
from .models import Achievement
from .serializers import (
    UserSerializer, 
    AchievementSerializer, 
    LoginSerializer,
    PasswordResetRequestSerializer,
    PasswordResetConfirmSerializer,
    ChangePasswordSerializer
)
from rest_framework import generics
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework.permissions import AllowAny
from core.mixins import ResponseMixin
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse
from django.template.loader import render_to_string

User = get_user_model()

class UserViewSet(ResponseMixin, viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.action in ['list', 'retrieve']:
            return User.objects.all()
        if self.request.user.is_authenticated:
            return User.objects.filter(id=self.request.user.id)
        return User.objects.none()  # Return an empty queryset if not authenticated

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return self.success_response(
            data=serializer.data,
            message="Users retrieved successfully"
        )

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return self.success_response(
            data=serializer.data,
            message="User details retrieved successfully"
        )

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            self.perform_create(serializer)
            return self.success_response(
                data=serializer.data,
                message="User created successfully",
                status_code=status.HTTP_201_CREATED
            )
        return self.error_response(
            message="Failed to create user",
            errors=serializer.errors
        )

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        if serializer.is_valid():
            self.perform_update(serializer)
            return self.success_response(
                data=serializer.data,
                message="User updated successfully"
            )
        return self.error_response(
            message="Failed to update user",
            errors=serializer.errors
        )

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return self.success_response(
            message="User deleted successfully",
            status_code=status.HTTP_204_NO_CONTENT
        )

    @action(detail=False, methods=['get'])
    def me(self, request):
        serializer = self.get_serializer(request.user)
        return self.success_response(
            data=serializer.data,
            message="User profile retrieved successfully"
        )

    @action(detail=True, methods=['get'])
    def achievements(self, request, pk=None):
        user = self.get_object()
        achievements = Achievement.objects.filter(user=user)
        serializer = AchievementSerializer(achievements, many=True)
        return self.success_response(
            data=serializer.data,
            message="User achievements retrieved successfully"
        )

    @action(detail=True, methods=['post'])
    def update_points(self, request, pk=None):
        if not request.user.is_authenticated:
            return self.error_response(
                message="Authentication required",
                status_code=status.HTTP_401_UNAUTHORIZED
            )

        user = self.get_object()
        points = request.data.get('points', 0)
        
        if points:
            user.points += points
            user.save()
            
        return self.success_response(
            data={'points': user.points},
            message="Points updated successfully"
        )
    
    @action(detail=False, methods=['post'])
    def change_password(self, request):
        user = request.user
        serializer = ChangePasswordSerializer(data=request.data)
        
        if serializer.is_valid():
            # Check old password
            if not user.check_password(serializer.validated_data['old_password']):
                return self.error_response(
                    message="Old password is incorrect",
                    status_code=status.HTTP_400_BAD_REQUEST
                )
                
            # Set new password
            user.set_password(serializer.validated_data['new_password'])
            user.save()
            
            return self.success_response(
                message="Password changed successfully"
            )
        
        return self.error_response(
            message="Failed to change password",
            errors=serializer.errors
        )

class SignupView(ResponseMixin, generics.CreateAPIView):
    serializer_class = UserSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return self.success_response(
                data={'user': UserSerializer(user).data},
                message="User registered successfully",
                status_code=status.HTTP_201_CREATED
            )
        return self.error_response(
            message="Registration failed",
            errors=serializer.errors
        )

class LoginView(ResponseMixin, generics.GenericAPIView):
    serializer_class = LoginSerializer
    permission_classes = [AllowAny]
    
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            username = serializer.validated_data['username']
            password = serializer.validated_data['password']
            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)  # Optional if you want to maintain session
                access_token = AccessToken.for_user(user)  # Generate JWT token
                return self.success_response(
                    data={'access': str(access_token)},
                    message="Login successful"
                )
            return self.error_response(
                message="Invalid credentials",
                status_code=status.HTTP_401_UNAUTHORIZED
            )
        return self.error_response(
            message="Login failed",
            errors=serializer.errors
        )

class PasswordResetRequestView(ResponseMixin, generics.GenericAPIView):
    serializer_class = PasswordResetRequestSerializer
    permission_classes = [AllowAny]
    
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            try:
                user = User.objects.get(email=email)
                
                # Generate token and uid
                token = default_token_generator.make_token(user)
                uid = urlsafe_base64_encode(force_bytes(user.pk))
                
                # Build reset URL (frontend URL)
                reset_url = f"{settings.FRONTEND_URL}/reset-password/{uid}/{token}/"
                
                # Send email
                subject = "Password Reset Request"
                message = f"Click the link below to reset your password:\n{reset_url}"
                email_from = settings.DEFAULT_FROM_EMAIL
                recipient_list = [user.email]
                
                send_mail(subject, message, email_from, recipient_list)
                
                return self.success_response(
                    message="Password reset link sent to your email"
                )
            except User.DoesNotExist:
                # For security reasons, don't reveal that the email doesn't exist
                return self.success_response(
                    message="If your email exists in our system, you will receive a password reset link"
                )
        
        return self.error_response(
            message="Invalid request",
            errors=serializer.errors
        )

class PasswordResetConfirmView(ResponseMixin, generics.GenericAPIView):
    serializer_class = PasswordResetConfirmSerializer
    permission_classes = [AllowAny]
    
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            try:
                uid = force_str(urlsafe_base64_decode(serializer.validated_data['uidb64']))
                user = User.objects.get(pk=uid)
                
                # Check if token is valid
                if default_token_generator.check_token(user, serializer.validated_data['token']):
                    # Set new password
                    user.set_password(serializer.validated_data['new_password'])
                    user.save()
                    
                    return self.success_response(
                        message="Password has been reset successfully"
                    )
                else:
                    return self.error_response(
                        message="Invalid or expired token",
                        status_code=status.HTTP_400_BAD_REQUEST
                    )
            except (TypeError, ValueError, OverflowError, User.DoesNotExist):
                return self.error_response(
                    message="Invalid user ID",
                    status_code=status.HTTP_400_BAD_REQUEST
                )
        
        return self.error_response(
            message="Password reset failed",
            errors=serializer.errors
        )
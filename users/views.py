from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth import get_user_model, authenticate, login
from .models import Achievement
from .serializers import UserSerializer, AchievementSerializer
from rest_framework import generics
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework.permissions import AllowAny  

User = get_user_model()

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.action in ['list', 'retrieve']:
            return User.objects.all()
        if self.request.user.is_authenticated:
            return User.objects.filter(id=self.request.user.id)
        return User.objects.none()  # Return an empty queryset if not authenticated

    @action(detail=False, methods=['get'])
    def me(self, request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def achievements(self, request, pk=None):
        user = self.get_object()
        achievements = Achievement.objects.filter(user=user)
        serializer = AchievementSerializer(achievements, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def update_points(self, request, pk=None):
        if not request.user.is_authenticated:
            return Response({'error': 'Authentication required.'}, status=status.HTTP_401_UNAUTHORIZED)

        user = self.get_object()
        points = request.data.get('points', 0)
        
        if points:
            user.points += points
            user.save()
            
        return Response({'points': user.points})

class SignupView(generics.CreateAPIView):
    serializer_class = UserSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response({'user': UserSerializer(user).data}, status=status.HTTP_201_CREATED)

class LoginView(generics.GenericAPIView):
    serializer_class = UserSerializer  # You can create a separate serializer for login if needed
    permission_classes = [AllowAny] 
    def post(self, request, *args, **kwargs):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)  # Optional if you want to maintain session
            access_token = AccessToken.for_user(user)  # Generate JWT token
            return Response({'access': str(access_token)}, status=status.HTTP_200_OK)
        return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
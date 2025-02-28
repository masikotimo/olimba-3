from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Sum
from .models import GameType, Question, Score, GameSession
from .serializers import (
    GameTypeSerializer, 
    QuestionSerializer,
    ScoreSerializer,
    GameSessionSerializer
)

class GameTypeViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = GameType.objects.all()
    serializer_class = GameTypeSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

class QuestionViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = QuestionSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        game_type = self.request.query_params.get('game_type', '')
        difficulty = self.request.query_params.get('difficulty', '')
        limit = int(self.request.query_params.get('limit', 10))
        
        queryset = Question.objects.all()
        
        if game_type:
            queryset = queryset.filter(game_type__name=game_type)
        if difficulty:
            queryset = queryset.filter(difficulty=difficulty)
            
        return queryset.order_by('?')[:limit]

class ScoreViewSet(viewsets.ModelViewSet):
    serializer_class = ScoreSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_authenticated:
            return Score.objects.filter(user=self.request.user)
        return Score.objects.none()  # Return an empty queryset if not authenticated

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['get'])
    def leaderboard(self, request):
        game_type = request.query_params.get('game_type', '')
        limit = int(request.query_params.get('limit', 10))
        
        queryset = Score.objects.values('user__username')\
            .annotate(total_score=Sum('points'))\
            .order_by('-total_score')
            
        if game_type:
            queryset = queryset.filter(game_type__name=game_type)
            
        return Response(queryset[:limit])

class GameSessionViewSet(viewsets.ModelViewSet):
    serializer_class = GameSessionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_authenticated:
            return GameSession.objects.filter(scores__user=self.request.user).distinct()
        return GameSession.objects.none()  # Return an empty queryset if not authenticated

    def perform_create(self, serializer):
        session = serializer.save()
        if 'scores' in self.request.data:
            for score_data in self.request.data['scores']:
                session.scores.create(
                    user=self.request.user,
                    score=score_data['score']
                )
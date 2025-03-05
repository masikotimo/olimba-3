from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Sum
from .models import GameType, Question, Score, GameSession, ScriptureSprintQuestion, FindTheBibleVerseQuestion, BibleCharadesQuestion, VerseVersion
from .serializers import (
    GameTypeSerializer, 
    QuestionSerializer,
    ScoreSerializer,
    GameSessionSerializer,
    ScriptureSprintQuestionSerializer,
    FindTheBibleVerseQuestionSerializer,
    BibleCharadesQuestionSerializer,
    VerseVersionSerializer
)
from core.mixins import ResponseMixin

class GameTypeViewSet(ResponseMixin, viewsets.ReadOnlyModelViewSet):
    queryset = GameType.objects.all()
    serializer_class = GameTypeSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return self.success_response(
            data=serializer.data,
            message="Game types retrieved successfully"
        )

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return self.success_response(
            data=serializer.data,
            message="Game type details retrieved successfully"
        )

class QuestionViewSet(ResponseMixin, viewsets.ReadOnlyModelViewSet):
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
    
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return self.success_response(
            data=serializer.data,
            message="Questions retrieved successfully"
        )

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return self.success_response(
            data=serializer.data,
            message="Question details retrieved successfully"
        )

class ScoreViewSet(ResponseMixin, viewsets.ModelViewSet):
    serializer_class = ScoreSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_authenticated:
            return Score.objects.filter(user=self.request.user)
        return Score.objects.none()  # Return an empty queryset if not authenticated

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return self.success_response(
            data=serializer.data,
            message="Scores retrieved successfully"
        )

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return self.success_response(
            data=serializer.data,
            message="Score details retrieved successfully"
        )

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            self.perform_create(serializer)
            return self.success_response(
                data=serializer.data,
                message="Score created successfully",
                status_code=201
            )
        return self.error_response(
            message="Failed to create score",
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
                message="Score updated successfully"
            )
        return self.error_response(
            message="Failed to update score",
            errors=serializer.errors
        )

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return self.success_response(
            message="Score deleted successfully",
            status_code=204
        )

    @action(detail=False, methods=['get'])
    def leaderboard(self, request):
        game_type = request.query_params.get('game_type', '')
        limit = int(request.query_params.get('limit', 10))
        
        queryset = Score.objects.values('user__username')\
            .annotate(total_score=Sum('points'))\
            .order_by('-total_score')
            
        if game_type:
            queryset = queryset.filter(game_type__name=game_type)
            
        return self.success_response(
            data=list(queryset[:limit]),
            message="Leaderboard retrieved successfully"
        )

class GameSessionViewSet(ResponseMixin, viewsets.ModelViewSet):
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
    
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return self.success_response(
            data=serializer.data,
            message="Game sessions retrieved successfully"
        )

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return self.success_response(
            data=serializer.data,
            message="Game session details retrieved successfully"
        )

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            self.perform_create(serializer)
            return self.success_response(
                data=serializer.data,
                message="Game session created successfully",
                status_code=201
            )
        return self.error_response(
            message="Failed to create game session",
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
                message="Game session updated successfully"
            )
        return self.error_response(
            message="Failed to update game session",
            errors=serializer.errors
        )

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return self.success_response(
            message="Game session deleted successfully",
            status_code=204
        )

class ScriptureSprintQuestionViewSet(ResponseMixin, viewsets.ReadOnlyModelViewSet):
    queryset = ScriptureSprintQuestion.objects.all()
    serializer_class = ScriptureSprintQuestionSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    @action(detail=True, methods=['post'])
    def add_version(self, request, pk=None):
        question = self.get_object()
        serializer = VerseVersionSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(verse=question)
            return self.success_response(
                data=serializer.data,
                message="Verse version added successfully",
                status_code=201
            )
        return self.error_response(
            message="Failed to add verse version",
            errors=serializer.errors
        )

class FindTheBibleVerseQuestionViewSet(ResponseMixin, viewsets.ReadOnlyModelViewSet):
    queryset = FindTheBibleVerseQuestion.objects.all()
    serializer_class = FindTheBibleVerseQuestionSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

class BibleCharadesQuestionViewSet(ResponseMixin, viewsets.ReadOnlyModelViewSet):
    queryset = BibleCharadesQuestion.objects.all()
    serializer_class = BibleCharadesQuestionSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
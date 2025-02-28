from rest_framework import serializers
from .models import GameType, Question, QuestionOption, Score, GameSession, SessionScore

class QuestionOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuestionOption
        fields = ['id', 'text', 'is_correct']

class QuestionSerializer(serializers.ModelSerializer):
    options = QuestionOptionSerializer(many=True, read_only=True)
    
    class Meta:
        model = Question
        fields = ['id', 'title', 'description', 'scripture', 'difficulty', 'options']

class GameTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = GameType
        fields = ['id', 'name', 'description', 'min_players', 'max_players', 'difficulty']

class ScoreSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    game_name = serializers.CharField(source='game_type.name', read_only=True)

    class Meta:
        model = Score
        fields = ['id', 'username', 'game_name', 'points', 'timestamp']

class GameSessionSerializer(serializers.ModelSerializer):
    scores = serializers.SerializerMethodField()

    class Meta:
        model = GameSession
        fields = ['id', 'game_type', 'start_time', 'end_time', 'status', 'scores']

    def get_scores(self, obj):
        return SessionScoreSerializer(obj.scores.all(), many=True).data

class SessionScoreSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = SessionScore
        fields = ['id', 'username', 'score', 'timestamp']
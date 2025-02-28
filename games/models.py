from django.db import models
from users.models import User

class GameType(models.Model):
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField()
    min_players = models.IntegerField(default=1)
    max_players = models.IntegerField()
    difficulty = models.CharField(
        max_length=20,
        choices=[
            ('easy', 'Easy'),
            ('medium', 'Medium'),
            ('hard', 'Hard')
        ]
    )

class Question(models.Model):
    game_type = models.ForeignKey(GameType, on_delete=models.CASCADE, related_name='questions')
    title = models.CharField(max_length=200)
    description = models.TextField()
    scripture = models.CharField(max_length=100)
    difficulty = models.CharField(
        max_length=20,
        choices=[
            ('easy', 'Easy'),
            ('medium', 'Medium'),
            ('hard', 'Hard')
        ]
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['?']  # Random ordering by default

class QuestionOption(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='options')
    text = models.CharField(max_length=200)
    is_correct = models.BooleanField(default=False)

    class Meta:
        ordering = ['?']  # Random ordering for options

class Score(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='scores')
    game_type = models.ForeignKey(GameType, on_delete=models.CASCADE)
    points = models.IntegerField()
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-points', '-timestamp']

class GameSession(models.Model):
    game_type = models.ForeignKey(GameType, on_delete=models.CASCADE)
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(null=True, blank=True)
    status = models.CharField(
        max_length=20,
        choices=[
            ('in_progress', 'In Progress'),
            ('completed', 'Completed'),
            ('abandoned', 'Abandoned')
        ],
        default='in_progress'
    )

class SessionScore(models.Model):
    session = models.ForeignKey(GameSession, on_delete=models.CASCADE, related_name='scores')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    score = models.IntegerField()
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-score', '-timestamp']
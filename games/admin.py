from django.contrib import admin
from .models import GameType, Question, QuestionOption, Score, GameSession, SessionScore

class QuestionOptionInline(admin.TabularInline):
    model = QuestionOption
    extra = 4

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('title', 'game_type', 'difficulty', 'created_at')
    list_filter = ('game_type', 'difficulty')
    search_fields = ('title', 'description')
    inlines = [QuestionOptionInline]

@admin.register(GameType)
class GameTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'difficulty', 'min_players', 'max_players')
    list_filter = ('difficulty',)
    search_fields = ('name', 'description')

@admin.register(Score)
class ScoreAdmin(admin.ModelAdmin):
    list_display = ('user', 'game_type', 'points', 'timestamp')
    list_filter = ('game_type', 'timestamp')
    search_fields = ('user__username',)

@admin.register(GameSession)
class GameSessionAdmin(admin.ModelAdmin):
    list_display = ('game_type', 'start_time', 'end_time', 'status')
    list_filter = ('game_type', 'status')

@admin.register(SessionScore)
class SessionScoreAdmin(admin.ModelAdmin):
    list_display = ('session', 'user', 'score', 'timestamp')
    list_filter = ('timestamp',)
    search_fields = ('user__username',)
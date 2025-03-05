from django.contrib import admin
from .models import GameType, Question, QuestionOption, Score, GameSession, SessionScore, ScriptureSprintQuestion, FindTheBibleVerseQuestion, BibleCharadesQuestion, VerseVersion

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
    list_display = ('name', 'description', 'min_players', 'max_players', 'difficulty')
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

@admin.register(ScriptureSprintQuestion)
class ScriptureSprintQuestionAdmin(admin.ModelAdmin):
    list_display = ('verse', 'description', 'pack_type', 'game_type')
    search_fields = ('verse', 'description')
    list_filter = ('game_type',)

@admin.register(FindTheBibleVerseQuestion)
class FindTheBibleVerseQuestionAdmin(admin.ModelAdmin):
    list_display = ('reference', 'text', 'book', 'chapter', 'verse', 'game_type')
    search_fields = ('reference', 'text', 'book')
    list_filter = ('game_type',)

@admin.register(BibleCharadesQuestion)
class BibleCharadesQuestionAdmin(admin.ModelAdmin):
    list_display = ('title', 'description', 'scripture', 'difficulty', 'game_type')
    search_fields = ('title', 'description', 'scripture')
    list_filter = ('game_type', 'difficulty')

@admin.register(VerseVersion)
class VerseVersionAdmin(admin.ModelAdmin):
    list_display = ('verse', 'translation', 'text')
    search_fields = ('verse__verse', 'translation')  # Allows searching by verse and translation
    list_filter = ('translation',)
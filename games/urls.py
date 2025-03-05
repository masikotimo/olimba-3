from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'games', views.GameTypeViewSet)
router.register(r'scripture-sprint-questions', views.ScriptureSprintQuestionViewSet, basename='scripture-sprint-question')
router.register(r'find-the-bible-verse-questions', views.FindTheBibleVerseQuestionViewSet, basename='find-the-bible-verse-question')
router.register(r'bible-charades-questions', views.BibleCharadesQuestionViewSet, basename='bible-charades-question')

urlpatterns = [
    path('', include(router.urls)),
]
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'games', views.GameTypeViewSet)
router.register(r'questions', views.QuestionViewSet, basename='question')
router.register(r'scores', views.ScoreViewSet, basename='score')
router.register(r'sessions', views.GameSessionViewSet, basename='session')

urlpatterns = [
    path('', include(router.urls)),
]
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'users', views.UserViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('signup/', views.SignupView.as_view(), name='signup'),
    path('login/', views.LoginView.as_view(), name='login'),
]
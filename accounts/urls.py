from django.urls import path
from .views import RegisterView,ProfileView
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
)

urlpatterns = [
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('register/', RegisterView.as_view(), name='register'),
    path('profile/', ProfileView.as_view(), name='profile'),
]

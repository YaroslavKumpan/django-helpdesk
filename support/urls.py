from django.urls import path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView

from .views import CustomTokenObtainPairView
from .api import (
    UserRegistrationView,
    SupportRequestViewSet,
    LogoutView,
    CurrentUserProfileView,
)

router = DefaultRouter()
router.register(r'requests', SupportRequestViewSet, basename='supportrequest')

urlpatterns = [
    path('register/', UserRegistrationView.as_view(), name='register'),
    path('login/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('profile/', CurrentUserProfileView.as_view(), name='current-profile'),
]

urlpatterns += router.urls

from django.urls import path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView

from .api import (
    UserRegistrationView,
    UserLoginView,
    SupportRequestViewSet,
)

router = DefaultRouter()
router.register(r'requests', SupportRequestViewSet, basename='supportrequest')

urlpatterns = [
    path('register/', UserRegistrationView.as_view(), name='register'),
    path('login/', UserLoginView.as_view(), name='login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]

urlpatterns += router.urls

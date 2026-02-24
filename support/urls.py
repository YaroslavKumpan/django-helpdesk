from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api import UserRegistrationView, UserLoginView, SupportRequestViewSet

router = DefaultRouter()
router.register(r'requests', SupportRequestViewSet, basename='supportrequest')

urlpatterns = [
    path('register/', UserRegistrationView.as_view(), name='register'),
    path('login/', UserLoginView.as_view(), name='login'),
]

urlpatterns += router.urls
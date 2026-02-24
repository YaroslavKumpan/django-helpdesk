from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.contrib.messages.storage.cookie import MessageSerializer
from rest_framework import serializers, request
from rest_framework.validators import UniqueValidator
from rest_framework_simplejwt.tokens import RefreshToken

from .models import UserProfile, SupportRequest

class UserRegistrationSerializer(serializers.ModelSerializer):
    # Валидация уникальности для username и email
    username = serializers.CharField(
        max_length=100,
        validators=[UniqueValidator(queryset=User.objects.all())],
    )
    email = serializers.EmailField(
        validators=[UniqueValidator(queryset=User.objects.all())],
    )

    password = serializers.CharField(write_only=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True)

    def validate(self, data):
        # Проверяем, что пароли совпадают
        if data["password"] != data["password2"]:
            raise serializers.ValidationError({"password2": "Пароли должны совпадать."})
        return data

    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'password2')
        extra_kwargs = {"password": {"write_only": True}, "password2": {"write_only": True}}

    def create(self, validated_data):
        validated_data.pop("password2")
        # создаем новогопользователя
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
        )
        return user

class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

    def validate(self, data):
        username = data.get('username')
        password = data.get('password')

        # Проверка существования пользователя
        user = User.objects.filter(username=username).first()
        if user is None:
            raise serializers.ValidationError("Неверные учетные данные: пользователь не найден.")

        # Проверка правильности пароля
        if not user.check_password(password):
            raise serializers.ValidationError("Неверные учетные данные: неверный пароль.")

        # генерим JWT токен
        refresh = RefreshToken.for_user(user)
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }


class UserProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = UserProfile
        fields = ['id', 'username', 'role', 'is_support']
        read_only_fields = ['id', 'username', 'is_support']  # is_support — property, только чтение


class SupportRequestSerializer(serializers.ModelSerializer):
    user - UserProfileSerializer(read_only=True)
    messages = MessageSerializer(many=True, read_only=True)

    class Meta:
        model = SupportRequest
        fields = [
            'id', 'title', 'description', 'status',
            'created_at', 'updated_at', 'user', 'messages',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def create(self, validated_data):
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['user'] = request.user
        else:
            raise serializers.ValidationError("User must be authenticated")
        return super().create(validated_data)

class SupportMessageSerializer(serializers.ModelSerializer):

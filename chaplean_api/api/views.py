import string
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User

from .serializers import RegisterSerializer, LoginSerializer

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer

class LoginView(APIView):
    serializer_class = LoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data
        token, created = Token.objects.get_or_create(user=user)
        return Response({"token": token.key}, status=status.HTTP_200_OK)


from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth.models import User
from django.core.cache import cache
from .serializers import PasswordResetRequestSerializer, PasswordResetSerializer
import random

class PasswordResetRequestView(APIView):
    serializer_class = PasswordResetRequestSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']

        # 4 haneli bir doğrulama kodu oluştur
        code = ''.join(random.choices(string.digits, k=4))
        cache.set(email, code, timeout=600)  # Kodu 10 dakika boyunca sakla

        # Doğrulama kodunu e-posta ile gönder (bu kısmı projeye göre özelleştirin)
        # send_mail(
        #     'Password Reset Code',
        #     f'Your password reset code is {code}',
        #     'from@example.com',
        #     [email],
        #     fail_silently=False,
        # )
        print(code)

        return Response({"detail": "Password reset code sent"}, status=status.HTTP_200_OK)

class PasswordResetView(APIView):
    serializer_class = PasswordResetSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        code = serializer.validated_data['code']
        new_password = serializer.validated_data['new_password']

        # Cache'den kodu al ve doğrula
        cached_code = cache.get(email)
        if cached_code != code:
            return Response({"detail": "Error false auth pass"}, status=status.HTTP_400_BAD_REQUEST)

        # Şifreyi güncelle
        user = User.objects.get(email=email)
        user.set_password(new_password)
        user.save()

        return Response({"detail": "Password has been reset"}, status=status.HTTP_200_OK)

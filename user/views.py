from random import randint
import threading

from django.contrib.auth import authenticate
from django.utils import timezone

from datetime import timedelta

from rest_framework import generics
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

from user.models import UserModel, FollowModel
from user.serializers import RegisterSerializers, ResendCodeSerializer, VerifyEmailSerializer, LoginSerializers, UserSerializer, FollowSerializer
from user.utils import send_email_verification


class RegisterViews(generics.CreateAPIView):
    serializer_class = RegisterSerializers
    queryset = UserModel.objects.all()
    permission_classes = [AllowAny]

    def perform_create(self, serializer):
        user = serializer.save()
        user.set_password(serializer.validated_data['password'])
        verification_code = str(randint(1000, 9999))  
        user.verification_code_created_at = timezone.now() 
        user.verification_code = verification_code
        user.is_active = False
        user.save()

        threading.Thread(target=send_email_verification, args=(user, verification_code)).start()

        return user


class VerifiyViews(APIView):
    permission_classes = [AllowAny]
    serializer_class = VerifyEmailSerializer

    def post(self, request):
        serializer = VerifyEmailSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = serializer.validated_data['user'] 
        user.is_active = True
        user.save()  
        response = {
            "success": True,
            "message": "Email verified successfully"
        }

        return Response(response, status=status.HTTP_200_OK)
    

class LoginView(generics.GenericAPIView):
    serializer_class = LoginSerializers
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        username = serializer.validated_data.get('username')
        email = serializer.validated_data.get('email')
        password = serializer.validated_data['password']
        print(username)
        print(password)
        
        user = None
        
        if username:  
            user = authenticate(username=username, password=password)
        if email and not user:
            try:
                user = UserModel.objects.get(email=email)
                user = authenticate(username=user.username, password=password)
            except UserModel.DoesNotExist:
                user = None
        
        if user is not None:
            refresh = RefreshToken.for_user(user)
            refresh.set_exp(lifetime=timedelta(minutes=10))
            refresh.access_token.set_exp(lifetime=timedelta(minutes=3))
            
            user.last_login = timezone.now()
            user.save()

            response = {
                "refresh_token": str(refresh),
                "access_token": str(refresh.access_token),
                "email": user.email,
                "username": user.username  
            }
            return Response(response, status=status.HTTP_200_OK)
        
        return Response({
            "success": False,
            "message": "Invalid credentials"
        }, status=status.HTTP_400_BAD_REQUEST)
    
    
class ResendCodeView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = ResendCodeSerializer(data=request.data)
        if serializer.is_valid():
            return Response({"message": "Verification code has been resent successfully!"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class ProfileView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer
    queryset = UserModel.objects.all()

    def get_object(self):
        return self.request.user
    

class FollowerView(APIView):
    serializer = FollowSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = FollowSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = self.request.user
        to_user = serializer.validate_data['to_user']
        response = {'success': True}

        following = FollowModel.objects.filter(user=user, to_user=to_user)
        
        if following.exists():
            following.delete()
            response['detail'] = "You have unfollowed this user."
            return Response(response, status=status.HTTP_204_NO_CONTENT)
        
        FollowModel.objects.create(user=user, to_user=to_user)
        
        response['detail'] = "You have followed this user."
        return Response(response, status=status.HTTP_201_CREATED) 

    def get(self, request):
        follow_type = self.request.query_params.get('type')
        qs = self.request.user.following.all()
        if follow_type == 'followers':
            qs = self.request.user.followers.all()
        serializer = FollowSerializer(qs, many=True, context={'request': self.request})
        return Response(serializer.data, status=status.HTTP_200_OK)
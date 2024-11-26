import random
import threading

from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from user.models import FollowModel, UserModel
from user.utils import send_email_verification

from django.utils import timezone

from datetime import timedelta


class RegisterSerializers(serializers.ModelSerializer):
    confirm_password = serializers.CharField(write_only=True)
    first_name = serializers.CharField(write_only=True, max_length=64)
    last_name = serializers.CharField(write_only=True, max_length=64)
    email = serializers.EmailField(max_length=254, validators=[
        UniqueValidator(queryset=UserModel.objects.all(), message='This email is already registered')
    ])


    class Meta:
        model = UserModel
        fields = ['id','first_name', 'last_name', 'username','email', 'password', 'confirm_password']
        extra_kwargs = {'password': {'write_only': True}}

    
    def validate(self, attrs):
        password = attrs.get('password')
        confirm_password = attrs.get('confirm_password')
        if password != confirm_password:
            raise serializers.ValidationError("Passwords do not match.")
        return attrs
    

    def validate_email(self, email: str):
        email = email.strip()
        if '@' not in email or '.' not in email.split('@')[-1]:
            raise serializers.ValidationError("Invalid email format. Please enter a valid email address.")
        return email
    

    def create(self, validated_data):
        validated_data.pop('confirm_password')  
        user = UserModel.objects.create_user(**validated_data)  
        user.is_active = False 
        user.set_password(validated_data['password'])
        user.save()
        return user 
    
    def generate_verification_code(self):
        self.verification_code = str(random.randint(1000, 9999))  
        self.verification_code_created_at = timezone.now()  
        self.save()
        return self.verification_code  
    
    
class LoginSerializers(serializers.Serializer):
    username = serializers.CharField(max_length=255)
    email = serializers.EmailField(max_length=255, required=False)
    password = serializers.CharField(max_length=255, write_only=True)


class VerifyEmailSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    verification_code = serializers.CharField(max_length=4, required=True)

    def validate(self, data):
        email = data.get('email')
        verification_code = data.get('verification_code')
        
        try:
            user = UserModel.objects.get(email=email)
        except UserModel.DoesNotExist:
            raise serializers.ValidationError("User not found!")
        if user.verification_code != verification_code:
            raise serializers.ValidationError("Invalid verification code!")
        
        current_time = timezone.now()
        if user.verification_code_created_at + timedelta(minutes=2) < current_time:
            raise serializers.ValidationError("Verification code expired!")
        
        data['user'] = user 
        return data
    

class ResendCodeSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate(self, attrs):
        email = attrs.get('email')
        
        try:
            user = UserModel.objects.get(email=email)
        except UserModel.DoesNotExist:
            raise serializers.ValidationError("User not found!")
        
        user.verification_code = str(random.randint(1000, 9999))  
        user.verification_code_created_at = timezone.now() 
        user.save()
        
        threading.Thread(target=send_email_verification, args=(user, user.verification_code)).start()
        
        return attrs


class FollowSerializer(serializers.ModelSerializer):
    to_user = serializers.PrimaryKeyRelatedField(queryset=UserModel.objects.all())

    class Meta:
        model = FollowModel
        fields = ['created_at', 'to_user']

    def is_follow_back(self, obj):
        follow_type = self.context.get('request').query_params.get('type')
        if follow_type == 'followers':
            return FollowModel.objects.filter(user=obj.user, to_user=obj.to_user).exists()
        return FollowModel.objects.filter(user=obj.to_user, to_user=obj.user).exists()

    def to_representation(self, instance):
        data = dict()
        data['first_name'] = instance.to_user.first_name
        data['last_name'] = instance.to_user.last_name
        data['email'] = instance.to_user.email
        data['username'] = instance.to_user.username
        data['follow_back'] = self.is_follow_back(instance)
        return data


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserModel
        exclude = ['password', 'groups', 'user_permissions', 'is_superuser']
        read_only_fields = ['is_active', 'date_joined', 'last_login', 'is_staff']

    def validate(self, attrs):
        user = self.context['request'].user
        to_user = attrs['to_user']
        if to_user == user:
            raise serializers.ValidationError("You can't follow yourself.")
        return attrs
from django.db import models
from django.contrib.auth.models import AbstractUser


class UserModel(AbstractUser):
    email = models.EmailField(unique=True)
    verification_code = models.CharField(max_length=4, blank=True, null=True)
    verification_code_created_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)


class FollowModel(models.Model):
    user = models.ForeignKey(UserModel, on_delete=models.CASCADE, related_name='following')
    to_user = models.ForeignKey(UserModel, on_delete=models.CASCADE, related_name='followers')

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} is following {self.to_user.username}"

    class Meta:
        ordering = ['-id'],
        verbose_name = 'Follower',
        verbose_name_plural = 'Followers'


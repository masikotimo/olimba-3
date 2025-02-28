from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models

class User(AbstractUser):
    points = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    groups = models.ManyToManyField(
        Group,
        related_name='custom_user_set',
        blank=True,
        help_text='The groups this user belongs to.',
        verbose_name='groups',
    )

    user_permissions = models.ManyToManyField(
        Permission,
        related_name='custom_user_permissions_set',
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions',
    )

    class Meta:
        ordering = ['-points']

class Achievement(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='achievements')
    title = models.CharField(max_length=100)
    description = models.TextField()
    unlocked_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-unlocked_at']
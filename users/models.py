from django.db import models
from django import forms
from django.contrib.auth.models import AbstractUser

# Create your models here.


class User(AbstractUser):
    username = models.CharField('Login', max_length=20, unique=True)
    password = models.CharField('Password', max_length=200)

    class Meta:
        permissions = (
            ('view', 'Просмотр'),
            ('edit', 'Изменение'),
        )

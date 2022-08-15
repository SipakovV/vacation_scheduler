from django.db import models
from django.contrib.auth.models import AbstractUser, Group
from .managers import CustomUserManager

# Create your models here.


class CustomUser(AbstractUser):
    first_name = None
    last_name = None
    department_manager = models.BooleanField(verbose_name='Является начальником отдела', default=False)
    bound_employee = models.OneToOneField('vacations.Employee', verbose_name='Привязанный сотрудник', blank=True, null=True, on_delete=models.SET_NULL)
    # department =

    objects = CustomUserManager()

    def __str__(self):
        if self.bound_employee is None:
            return self.username
        else:
            return str(self.bound_employee)

    class Meta:
        ordering = ['username']

'''
class Department(Group):
    title = models.CharField(verbose_name='Отдел', max_length=20, unique=True)
'''

from django.db import models
from django.contrib.auth.models import AbstractUser, Group

# Create your models here.


class User(AbstractUser):
    username = models.CharField(verbose_name='Логин', max_length=20, unique=True)
    password = models.CharField(verbose_name='Пароль', max_length=200)
    department_manager = models.BooleanField(verbose_name='Является начальником отдела', default=False)
    bound_employee = models.OneToOneField('vacations.Employee', verbose_name='Привязанный сотрудник', blank=True, null=True, on_delete=models.SET_NULL)
    # department =

    def __str__(self):
        if self.bound_employee is None:
            return self.username
        else:
            return str(self.username) + '(' + str(self.bound_employee.name) + ')'

    class Meta:
        ordering = ['username']

'''
class Department(Group):
    title = models.CharField(verbose_name='Отдел', max_length=20, unique=True)
'''

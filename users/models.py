from django.db import models
from django.contrib.auth.models import AbstractUser, Group
from .managers import CustomUserManager

# Create your models here.


class CustomUser(AbstractUser):
    DEFAULT = 0
    VIEW = 1
    EDIT = 2
    PERMISSIONS_CHOICES = (
        (DEFAULT, 'Нет специальных прав'),
        (VIEW, 'Просмотр данных'),
        (EDIT, 'Просмотр и изменение данных'),
    )

    first_name = None
    last_name = None
    is_department_manager = models.BooleanField(verbose_name='Является начальником отдела (может изменять отпуска)', default=False)
    bound_employee = models.OneToOneField('vacations.Employee', verbose_name='Привязанный сотрудник', blank=True, null=True, on_delete=models.SET_NULL)
    employees_permission_level = models.SmallIntegerField(verbose_name='Права на взаимодействие с данными сотрудников', choices=PERMISSIONS_CHOICES, default=DEFAULT)
    # = models.BooleanField(verbose_name='Может изменять данные сотрудников', default=False)
    #can_view_employees = models.BooleanField(verbose_name='Может просматривать данные сотрудников', default=False)

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

import datetime

from django.core.exceptions import ValidationError
from django.shortcuts import render
from django.db import models
from django.db.models.functions import ExtractMonth


class Department(models.Model):
    name = models.CharField(max_length=50, verbose_name='Название отдела')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'Отделы'
        verbose_name = 'Отдел'


class Employee(models.Model):
    name = models.CharField(max_length=50, verbose_name='ФИО')
    #login = models.OneToOneField('users.User', verbose_name='Логин', blank=True, null=True, on_delete=models.SET_NULL)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, verbose_name='ID отдела')
    replaces = models.ForeignKey('self', on_delete=models.SET_NULL, verbose_name='Замещает', default=None, blank=True,
                                 null=True)
    # replaces = models.IntegerField(verbose_name='ID замещаемых работников')
    rating = models.FloatField(verbose_name='Рейтинг', default=0)
    entry_date = models.DateField(verbose_name='Дата начала работы', default=datetime.date.min)
    vacation_days = models.IntegerField(verbose_name='Дней отпуска', default=38)

    def __str__(self):
        return self.name

    def change_rating(self, diff):
        self.rating += diff

    class Meta:
        verbose_name_plural = 'Работники'
        verbose_name = 'Работник'
        ordering = ['-rating']


class Vacation(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, verbose_name='Работник')
    start = models.DateField(verbose_name='Начало отпуска')
    end = models.DateField(verbose_name='Конец отпуска')

    def save(self, *args, **kwargs):
        empl = Employee.objects.get(pk=self.employee.pk)
        entry_anniversary = empl.entry_date
        new_year = datetime.date.today().year
        entry_anniversary = entry_anniversary.replace(year=new_year)
        if entry_anniversary > datetime.date.today():
            entry_anniversary = entry_anniversary.replace(year=new_year-1)
        if self.start > entry_anniversary:
            relevant_flag = True
        else:
            relevant_flag = False

        rating_coef = {
            1: 11,
            2: 12,
            3: 9,
            4: 7,
            5: 5,
            6: 3,
            7: 1,
            8: 2,
            9: 4,
            10: 6,
            11: 8,
            12: 10,
        }

        delta = datetime.timedelta(days=1)
        cur_date = self.start
        diff = 0

        while cur_date <= self.end:
            if cur_date.isoweekday() <= 5:
                if relevant_flag:
                    empl.vacation_days -= 1
                diff += rating_coef[cur_date.month]
            cur_date += delta

        empl.change_rating(diff)
        empl.save()

        super(Vacation, self).save(*args, **kwargs)

    class Meta:
        verbose_name_plural = 'Отпуска'
        verbose_name = 'Отпуск'
        ordering = ['start']

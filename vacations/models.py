import datetime
import logging
import copy
from logging.handlers import RotatingFileHandler

from django.core.exceptions import ValidationError
from django.shortcuts import render
from django.db import models
from django.db.models.functions import ExtractMonth
from django.contrib.postgres.fields import ArrayField

logger = logging.getLogger(__name__)

NEW_YEAR_DAY = 7
RATING_COEF = {
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


class Department(models.Model):
    title = models.CharField(max_length=50, verbose_name='Название отдела')

    vacation_days_by_month = ArrayField(
        models.IntegerField(default=0),
        size=12,
        default=list,
    )

    def __str__(self):
        return self.title

    def test_vacation_days(self):
        for i in range(12):
            self.vacation_days_by_month[i] = i*3
            logger.debug(self.vacation_days_by_month[i])

    def check_vacation_days(self, start, end):
        cur_date = start
        delta = datetime.timedelta(days=1)
        cur_month = 0
        test_days = 0
        #test_days = self.vacation_days_by_month.copy()
        while cur_date <= end:
            #logger.debug('cur_date=' + str(cur_date))
            if cur_date.isoweekday() <= 5:
                if cur_month != cur_date.month:
                    cur_month = cur_date.month
                    #logger.debug('cur_month=' + str(cur_month))
                    test_days = copy.copy(self.vacation_days_by_month[cur_month-1])
                if test_days < 0:
                    return False
                test_days -= 1
                #logger.debug('test_days=' + str(test_days) + ' ' + str(type(test_days)))
            cur_date += delta
        return True

    def change_vacation_days(self, start, end, reverse=False):
        cur_date = start
        delta = datetime.timedelta(days=1)
        cur_month = 0
        #logger.debug('feb_days_init=' + str(self.vacation_days_by_month[cur_month - 1]))
        while cur_date <= end:
            if cur_date.isoweekday() <= 5:
                cur_month = cur_date.month
                if reverse:
                    self.vacation_days_by_month[cur_month-1] += 1
                else:
                    self.vacation_days_by_month[cur_month-1] -= 1
                #logger.debug('feb_days=' + str(self.vacation_days_by_month[cur_month-1]))
            cur_date += delta
        self.save()

    class Meta:
        verbose_name_plural = 'Отделы'
        verbose_name = 'Отдел'


class Employee(models.Model):
    last_name = models.CharField(max_length=100, verbose_name='Фамилия')
    first_name = models.CharField(max_length=30, verbose_name='Имя')
    middle_name = models.CharField(max_length=50, verbose_name='Отчество')
    department = models.ForeignKey(Department, on_delete=models.CASCADE, verbose_name='Отдел')
    replaces = models.ForeignKey('self', on_delete=models.SET_NULL, verbose_name='Замещает', default=None, blank=True,
                                 null=True)
    rating = models.FloatField(verbose_name='Рейтинг', default=0)
    entry_date = models.DateField(verbose_name='Дата начала работы', default=datetime.date.min)
    vacation_days = models.IntegerField(verbose_name='Дней отпуска', default=38)

    def __str__(self):
        return str(self.last_name) + ' ' + str(self.first_name) + ' ' + str(self.middle_name)

    def change_vacation_days(self, start, end, reverse=False):
        cur_date = start
        delta = datetime.timedelta(days=1)
        while cur_date <= end:
            if cur_date.isoweekday() <= 5:
                if reverse:
                    self.vacation_days += 1
                else:
                    self.vacation_days -= 1
            cur_date += delta

    def change_rating(self, diff):
        self.rating += diff

    def reset_rating(self):
        self.rating = 0

    def reset_vacation_days(self):
        self.vacation_days = 38

    def save(self, *args, **kwargs):
        super(Employee, self).save(*args, **kwargs)
        logger.info('Employee added/edited: ' + str(self))

    class Meta:
        verbose_name_plural = 'Работники'
        verbose_name = 'Работник'
        ordering = ['department', '-rating']


class Vacation(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, verbose_name='Работник')
    start = models.DateField(verbose_name='Начало отпуска')
    end = models.DateField(verbose_name='Конец отпуска')

    def __str__(self):
        return str(self.start) + '-' + str(self.end) + ' (' + str(self.employee) + ')'

    def is_current_year(self):
        current_year = datetime.date.today().year
        vacation_year = getattr(self, 'start').year

        if vacation_year == current_year:
            return True
        else:
            return False

    def is_relevant(self):
        relevant_flag = False
        current_year = datetime.date.today().year

        relevance_date = datetime.date.today().replace(year=current_year - 3)
        # entry_anniversary = entry_anniversary.replace(year=current_year)
        # if entry_anniversary > datetime.date.today():
        #    entry_anniversary = entry_anniversary.replace(year=current_year-1)

        if getattr(self, 'start') > relevance_date:
            relevant_flag = True

        return relevant_flag

    def change_values(self, reverse=False):
        empl = Employee.objects.get(pk=self.employee.pk)
        start = getattr(self, 'start')
        end = getattr(self, 'end')

        logger.debug('change_values call')
        # entry_anniversary = empl.entry_date

        delta = datetime.timedelta(days=1)
        cur_date = start
        diff = 0

        while cur_date <= end:
            if cur_date.isoweekday() <= 5:
                #empl.vacation_days -= 1
                diff += RATING_COEF[cur_date.month]
            cur_date += delta

        if reverse:
            empl.change_rating(-diff)
        else:
            empl.change_rating(diff)

        if self.is_current_year():
            empl.department.change_vacation_days(start, end, reverse)
            empl.change_vacation_days(start, end, reverse)

        empl.save()

    def save(self, *args, **kwargs):
        empl = Employee.objects.get(pk=self.employee.pk)

        if self.is_relevant():
            self.change_values()

        super(Vacation, self).save(*args, **kwargs)
        logger.info('Vacation added: ' + str(empl) + ' ' + self.start.strftime('%m/%d/%Y') + '-' + self.end.strftime('%m/%d/%Y'))

    class Meta:
        verbose_name_plural = 'Отпуска'
        verbose_name = 'Отпуск'
        ordering = ['start']

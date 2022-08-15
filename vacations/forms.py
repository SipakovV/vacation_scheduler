from django.forms import ModelForm, SelectDateWidget, DateInput, Form, HiddenInput
from django.contrib.admin.widgets import AdminDateWidget
import datetime
import logging
from logging.handlers import RotatingFileHandler

from django.core.exceptions import ValidationError
from django.forms.fields import DateField, IntegerField

from .models import Employee, Vacation, Department

logger = logging.getLogger(__name__)


class DateInput(DateInput):
    input_type = "date"

    def __init__(self, **kwargs):
        #kwargs["format"] = "%Y-%m-%d"
        #kwargs["format"] = "%m-%d-%Y"
        super().__init__(**kwargs)


class EmployeeForm(ModelForm):
    class Meta:
        model = Employee
        fields = ('last_name', 'first_name', 'middle_name', 'department', 'replaces', 'entry_date', 'vacation_days')
        #exclude = ['rating']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["entry_date"].widget = DateInput(format='%d-%m-%Y')


class DepartmentForm(ModelForm):
    class Meta:
        model = Department
        fields = ('title',)


class VacationForm(ModelForm):

    class Meta:
        model = Vacation
        fields = ('start', 'end', 'employee')

    def __init__(self, *args, **kwargs):
        #print('kwargs(forms.init) = ', kwargs)
        super().__init__(*args, **kwargs)
        self.fields["employee"].widget = HiddenInput()
        self.fields["start"].widget = DateInput(format='%d-%m-%Y')
        self.fields["end"].widget = DateInput(format='%d-%m-%Y')
        #print('kwargs(forms.init).initial = ', kwargs['initial']['employee'])

    def clean(self):
        cleaned_data = super(VacationForm, self).clean()
        start = cleaned_data.get('start')
        end = cleaned_data.get('end')
        employee = cleaned_data.get('employee')
        #employee = Employee.objects.get(pk=employee_pk.pk)
        logger.debug(('clean ', employee))
        entry_anniversary = employee.entry_date
        new_year = datetime.date.today().year
        entry_anniversary = entry_anniversary.replace(year=new_year)
        if entry_anniversary > datetime.date.today():
            entry_anniversary = entry_anniversary.replace(year=new_year-1)
        if start > entry_anniversary:
            relevant_flag = True
        else:
            relevant_flag = False
            
        if employee.replaces is not None:
            replaced_empl = Employee.objects.get(pk=employee.replaces.pk)
            replaced_vacations = Vacation.objects.filter(employee=replaced_empl.pk)

        delta = datetime.timedelta(days=1)
        cur_date = start
        diff = 0

        vacation_days = employee.vacation_days

        while cur_date <= end:
            if cur_date.isoweekday() <= 5:
                if relevant_flag:
                    vacation_days -= 1
                    if vacation_days < 0:
                        raise ValidationError('Недостаточно отпускных!')
            cur_date += delta

        if start and end:
            if start >= end:
                raise ValidationError('Неправильный период!')
            if employee.replaces is not None:
                for vacation in replaced_vacations:
                    if start <= vacation.end <= end or start <= vacation.start <= end or start >= vacation.start and end <= vacation.end:
                        raise ValidationError('Замещаемый работник уже имеет отпуск в этот период!')

        # Always return the cleaned data, whether you have changed it or not.
        return cleaned_data




import datetime
import logging
import copy

from django.forms import ModelForm, SelectDateWidget, DateInput, Form, HiddenInput, forms
from django.contrib.admin.widgets import AdminDateWidget
from django.core.exceptions import ValidationError, NON_FIELD_ERRORS
from django.forms.fields import DateField, IntegerField, BooleanField

from .models import Employee, Vacation, Department, RELEVANT, ARCHIVE, PLANNED

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
        fields = ('personnel_number', 'last_name', 'first_name', 'middle_name', 'department', 'specialty', 'replaces',
                  'entry_date', 'max_vacation_days', 'vacation_days')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['entry_date'].widget = DateInput(format='%d-%m-%Y')
        self.fields['vacation_days'].widget = HiddenInput()
        self.fields['vacation_days'].required = False
        self.fields['vacation_days'].initial = 38

        for name in self.fields.keys():
            self.fields[name].widget.attrs.update({
                'class': 'form-control',
            })

    def clean(self):
        cleaned_data = super(EmployeeForm, self).clean()
        cleaned_data['vacation_days'] = cleaned_data['max_vacation_days']


class EmployeeUpdateForm(ModelForm):
    class Meta:
        model = Employee
        exclude = (
            'department',
            'vacation_days',
        )


class DepartmentForm(ModelForm):
    class Meta:
        model = Department
        fields = ('title', 'full_title')


class VacationForm(ModelForm):
    #forms.IntegerField(required = False)
    #force_proceed = BooleanField(initial=False)

    class Meta:
        model = Vacation
        fields = ('start', 'end', 'employee', 'relevance')
        error_messages = {
            #NON_FIELD_ERRORS: {
            'end': {
                'invalid_period': 'Неправильный период!',
                'vacation_days': 'Недостаточно отпускных!',
                'intersection': 'Заданный отпуск пересекается с уже имеющимся отпуском!',
                'replaced_employee': 'Замещаемый работник уже имеет отпуск в этот период!',
                'month_vacation_days': 'Недостаточно отпускных дней в месяце!',
            },
        }

    def __init__(self, *args, **kwargs):
        #print('kwargs(forms.init) = ', kwargs)
        super().__init__(*args, **kwargs)
        self.fields['employee'].widget = HiddenInput()
        self.fields['relevance'].widget = HiddenInput()
        self.fields['relevance'].required = False
        self.fields['start'].widget = DateInput(format='%d-%m-%Y')
        self.fields['end'].widget = DateInput(format='%d-%m-%Y')
        self.relevance_init = ARCHIVE
        #self.fields['force_proceed'].initial = False
        #print('kwargs(forms.init).initial = ', kwargs['initial']['employee'])

    def clean(self):
        cleaned_data = super(VacationForm, self).clean()
        start = cleaned_data.get('start')
        end = cleaned_data.get('end')
        employee = cleaned_data.get('employee')

        current_year = datetime.date.today().year
        relevance_date = datetime.date.today().replace(year=current_year - 3)
        relevant_flag = False
        current_year_flag = False

        cleaned_data['relevance'] = ARCHIVE

        if start > relevance_date:
            relevant_flag = True
            cleaned_data['relevance'] = RELEVANT

        if start.year == current_year:
            current_year_flag = True
            cleaned_data['relevance'] = PLANNED

        if 'force_proceed' in self.data:
            return cleaned_data

        logger.debug(('clean ', employee))

        own_vacations = Vacation.objects.filter(employee=employee.pk)

        delta = datetime.timedelta(days=1)
        cur_date = start
        diff = 0

        vacation_days = copy.copy(employee.vacation_days)

        # validation flags
        vacation_days_flag = False
        invalid_period_flag = False
        intersection_flag = False
        replaced_employee_flag = False
        month_vacation_days_flag = False

        if start and end:
            if start >= end:
                invalid_period_flag = True
                #raise ValidationError('Неправильный период!')

            if cleaned_data['relevance'] >= RELEVANT:
                for vacation in own_vacations:
                    if start <= vacation.end <= end or start <= vacation.start <= end or start >= vacation.start and \
                            end <= vacation.end:
                        intersection_flag = True
                        # raise ValidationError('Заданный отпуск пересекается с уже имеющимся отпуском!')

            if cleaned_data['relevance'] == PLANNED:
                while cur_date <= end:
                    if cur_date.isoweekday() <= 5:
                        if current_year_flag:
                            vacation_days -= 1
                            if vacation_days < 0:
                                vacation_days_flag = True
                                # raise ValidationError('Недостаточно отпускных!')
                    cur_date += delta

                if employee.replaces is not None:
                    replaced_empl = Employee.objects.get(pk=employee.replaces.pk)
                    replaced_vacations = Vacation.objects.filter(employee=replaced_empl.pk)
                    for vacation in replaced_vacations:
                        if start <= vacation.end <= end or start <= vacation.start <= end or start >= vacation.start and \
                                end <= vacation.end:
                            replaced_employee_flag = True
                            #raise ValidationError('Замещаемый работник уже имеет отпуск в этот период!')

                if current_year_flag:
                    vacation_days_valid = employee.department.check_vacation_days(start, end)
                    if not vacation_days_valid:
                        #employee.department.change_vacation_days(start, end)
                        month_vacation_days_flag = True
                        #raise ValidationError('Недостаточно отпускных дней в месяце!'

        errors_list = []

        if vacation_days_flag:
            errors_list.append(ValidationError(self.fields['end'].error_messages['vacation_days']))
        if invalid_period_flag:
            errors_list.append(ValidationError(self.fields['end'].error_messages['invalid_period']))
        if intersection_flag:
            errors_list.append(ValidationError(self.fields['end'].error_messages['intersection']))
        if replaced_employee_flag:
            errors_list.append(ValidationError(self.fields['end'].error_messages['replaced_employee']))
        if month_vacation_days_flag:
            errors_list.append(ValidationError(self.fields['end'].error_messages['month_vacation_days']))

        if errors_list:
            raise ValidationError(errors_list)

        return cleaned_data


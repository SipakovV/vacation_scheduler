
import datetime
import logging
import copy

from django.forms import ModelForm, SelectDateWidget, DateInput, Form, HiddenInput, forms
from django.contrib.admin.widgets import AdminDateWidget
from django.core.exceptions import ValidationError, NON_FIELD_ERRORS
from django.forms.fields import DateField, IntegerField, BooleanField

from .models import Employee, Vacation, Department, RELEVANT, ARCHIVE, PLANNED

logger = logging.getLogger(__name__)


class CustomDateInput(DateInput):
    input_type = "date"

    def __init__(self, **kwargs):
        #kwargs["format"] = "%Y-%m-%d"
        #kwargs['format'] = "%d-%m-%Y"
        super().__init__(**kwargs)


class EmployeeForm(ModelForm):
    class Meta:
        model = Employee
        fields = ('personnel_number', 'last_name', 'first_name', 'middle_name', 'department', 'specialty', 'replaces',
                  'entry_date', 'max_vacation_days', 'vacation_days')
        error_messages = {
            # NON_FIELD_ERRORS: {
            'replaces': {
                'different_department': 'Замещаемый сотрудник должен принадлежать тому же отделу!',
            },
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['entry_date'].widget = CustomDateInput(format='%d/%m/%Y')
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

        if 'force_proceed' in self.data:
            return cleaned_data

        errors_list = []
        if cleaned_data['replaces'] is not None:
            if cleaned_data['replaces'].department != cleaned_data['department']:
                errors_list.append(ValidationError(self.fields['replaces'].error_messages['different_department']))
        if errors_list:
            raise ValidationError(errors_list)

        return cleaned_data


class EmployeeUpdateForm(ModelForm):
    class Meta:
        model = Employee
        exclude = (
            'vacation_days',
            'rating',
        )
        error_messages = {
            # NON_FIELD_ERRORS: {
            'replaces': {
                'different_department': 'Замещаемый сотрудник должен принадлежать тому же отделу!',
                'replaces_self': 'Сотрудник не может замещать самого себя!',
            },
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['entry_date'].widget = DateInput(format='%d.%m.%Y')

        for name in self.fields.keys():
            self.fields[name].widget.attrs.update({
                'class': 'form-control',
            })

    def clean(self):
        cleaned_data = super(EmployeeUpdateForm, self).clean()

        if cleaned_data['replaces'] is not None:
            if cleaned_data['replaces'].pk == self.instance.pk:
                raise ValidationError((self.fields['replaces'].error_messages['replaces_self']))

        if 'force_proceed' in self.data:
            return cleaned_data

        errors_list = []

        if cleaned_data['replaces'] is not None:
            if cleaned_data['replaces'].department != cleaned_data['department']:
                errors_list.append(ValidationError(self.fields['replaces'].error_messages['different_department']))
        if errors_list:
            raise ValidationError(errors_list)
        return cleaned_data


class DepartmentForm(ModelForm):
    class Meta:
        model = Department
        fields = ('title', 'full_title')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name in self.fields.keys():
            self.fields[name].widget.attrs.update({
                'class': 'form-control',
            })


class VacationForm(ModelForm):
    class Meta:
        model = Vacation
        fields = ('start', 'end', 'employee', 'relevance')
        error_messages = {
            #NON_FIELD_ERRORS: {
            'end': {
                'far_future': 'Отпуск задан дальше, чем на следующий год!',
                'invalid_period': 'Неправильный период!',
                'vacation_days': 'Недостаточно отпускных!',
                'intersection': 'Заданный отпуск пересекается с уже имеющимся отпуском!',
                'replaced_employee': 'Замещаемый работник уже имеет отпуск в этот период!',
                'month_vacation_days': 'Недостаточно отпускных дней в месяце!',
            },
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['employee'].widget = HiddenInput()
        self.fields['relevance'].widget = HiddenInput()
        self.fields['relevance'].required = False
        self.fields['start'].widget = CustomDateInput(format='%d/%m/%Y')
        self.fields['end'].widget = CustomDateInput(format='%d/%m/%Y')
        self.relevance_init = ARCHIVE
        #self.fields['force_proceed'].initial = False
        #print('kwargs(forms.init).initial = ', kwargs['initial']['employee'])

        for name in self.fields.keys():
            self.fields[name].widget.attrs.update({
                'class': 'form-control',
            })

    def clean(self):
        cleaned_data = super(VacationForm, self).clean()
        start = cleaned_data.get('start')
        end = cleaned_data.get('end')
        employee = cleaned_data.get('employee')

        current_year = datetime.date.today().year
        relevance_year = current_year - 2
        relevant_flag = False
        current_year_flag = False

        cleaned_data['relevance'] = ARCHIVE

        if start.year >= relevance_year:
            relevant_flag = True
            cleaned_data['relevance'] = RELEVANT

        if start.year == current_year + 1:
            current_year_flag = True
            cleaned_data['relevance'] = PLANNED

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
        too_far_future_flag = False

        if start and end:
            if start >= end:
                invalid_period_flag = True
                #raise ValidationError('Неправильный период!')

            if 'force_proceed' in self.data and not invalid_period_flag:
                return cleaned_data

            if start.year > current_year + 1:
                too_far_future_flag = True

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

        if too_far_future_flag:
            errors_list.append(ValidationError(self.fields['end'].error_messages['far_future']))
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


from datetime import date
import logging
from calendar import monthrange

from django.shortcuts import render, get_object_or_404, redirect
from django.utils.decorators import method_decorator
from django.contrib import messages
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy, reverse

from .models import Employee, Department, Vacation
from .forms import VacationForm, EmployeeForm, DepartmentForm

from django.contrib.auth.decorators import login_required


logger = logging.getLogger(__name__)

DEFAULT = 0
VIEW = 1
EDIT = 2


class DepartmentCreateView(CreateView):
    template_name = 'vacations/add_department.html'
    form_class = DepartmentForm
    success_url = reverse_lazy('vacations:index')

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get(self, *args, **kwargs):
        user = self.request.user
        if not user.is_staff:
            if not (user.is_department_manager and user.employees_permission_level >= EDIT):  # ++ if not HR
                messages.warning(self.request, 'Недостаточно прав для добавления отдела')
                return redirect('vacations:index')
        return super(DepartmentCreateView, self).get(args, kwargs)

    def post(self, *args, **kwargs):
        user = self.request.user
        if not user.is_staff:
            if not (user.is_department_manager and user.employees_permission_level >= EDIT):  # ++ if not HR
                messages.warning(self.request, 'Недостаточно прав для добавления отдела')
                return redirect('vacations:index')
        return super(DepartmentCreateView, self).post(args, kwargs)


class DepartmentDeleteView(DeleteView):
    template_name = 'vacations/delete_department.html'
    model = Department
    success_url = reverse_lazy('vacations:index')

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get(self, *args, **kwargs):
        user = self.request.user
        if not user.is_staff:
            if not (user.is_department_manager and user.employees_permission_level >= EDIT):  # ++ if not HR
                messages.warning(self.request, 'Недостаточно прав для удаления отдела')
                return redirect('vacations:index')
        return super(DepartmentDeleteView, self).get(args, kwargs)

    def post(self, *args, **kwargs):
        user = self.request.user
        if not user.is_staff:
            if not (user.is_department_manager and user.employees_permission_level >= EDIT):  # ++ if not HR
                messages.warning(self.request, 'Недостаточно прав для удаления отдела')
                return redirect('vacations:index')
        return super(DepartmentDeleteView, self).post(args, kwargs)


class EmployeeCreateView(CreateView):
    template_name = 'vacations/add_employee.html'
    form_class = EmployeeForm
    success_url = reverse_lazy('vacations:index')

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get(self, *args, **kwargs):
        user = self.request.user
        if not user.is_staff:
            if not (user.employees_permission_level >= EDIT):  # ++ if not HR
                messages.warning(self.request, 'Недостаточно прав для добавления сотрудников')
                return redirect('vacations:index')
        return super(EmployeeCreateView, self).get(args, kwargs)

    def post(self, *args, **kwargs):
        user = self.request.user
        if not user.is_staff:
            if not (user.employees_permission_level >= EDIT):  # ++ if not HR
                messages.warning(self.request, 'Недостаточно прав для добавления сотрудников')
                return redirect('vacations:index')
        return super(EmployeeCreateView, self).post(args, kwargs)


class EmployeeUpdateView(UpdateView):
    template_name = 'vacations/edit_employee.html'
    success_url = reverse_lazy('vacations:index')
    model = Employee
    fields = ('department', 'replaces', 'entry_date', 'vacation_days')
    template_name_suffix = '_update_form'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get(self, *args, **kwargs):
        user = self.request.user

        if not user.is_staff:
            if not user.employees_permission_level >= EDIT:
                messages.warning(self.request, 'Недостаточно прав для редактирования данных сотрудников')
                return redirect('vacations:details', kwargs['pk'])
        return super(EmployeeUpdateView, self).get(args, kwargs)

    def post(self, *args, **kwargs):
        user = self.request.user

        if not user.is_staff:
            if not user.employees_permission_level >= EDIT:
                messages.warning(self.request, 'Недостаточно прав для редактирования данных сотрудников')
                return redirect('vacations:details', kwargs['pk'])
        return super(EmployeeUpdateView, self).post(args, kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['employee'] = Employee.objects.get(pk=int(self.kwargs['pk']))
        return context


class EmployeeDeleteView(DeleteView):
    template_name = 'vacations/delete_employee.html'
    model = Employee
    success_url = reverse_lazy('vacations:index')

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get(self, *args, **kwargs):
        user = self.request.user
        if not user.is_staff:
            if not user.employees_permission_level >= EDIT:  # ++ if not HR
                messages.warning(self.request, 'Недостаточно прав для удаления сотрудников')
                return redirect('vacations:details', kwargs['employee_id'])
        return super(EmployeeDeleteView, self).get(args, kwargs)

    def post(self, *args, **kwargs):
        user = self.request.user
        if not user.is_staff:
            if not user.employees_permission_level >= EDIT:  # ++ if not HR
                messages.warning(self.request, 'Недостаточно прав для удаления сотрудников')
                return redirect('vacations:details', kwargs['employee_id'])
        return super(EmployeeDeleteView, self).post(args, kwargs)


class VacationCreateView(CreateView):
    template_name = 'vacations/details.html'
    form_class = VacationForm
    #employee_id = '0'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get(self, *args, **kwargs):
        user = self.request.user
        if not user.is_staff:
            if not (user.employees_permission_level >= VIEW or user.bound_employee.pk == self.kwargs['employee_id'] or user.is_department_manager):
                messages.warning(self.request, 'Недостаточно прав для доступа к странице')
                return redirect('vacations:by_department', user.bound_employee.department.pk)
        return super(VacationCreateView, self).get(args, kwargs)

    def post(self, *args, **kwargs):
        user = self.request.user
        if not user.is_staff:
            if not user.is_department_manager:
                messages.warning(self.request, 'Недостаточно прав для добавления отпусков')
                return redirect('vacations:by_department', user.bound_employee.department.pk)
        return super(VacationCreateView, self).post(args, kwargs)

    def get_success_url(self):
        employee_id = self.kwargs['employee_id']
        #print('get_success_url employee_id = ', employee_id)
        return reverse_lazy('vacations:details', kwargs={'employee_id': employee_id})

    def get_initial(self, *args, **kwargs):
        initial = super(VacationCreateView, self).get_initial(**kwargs)
        initial['employee'] = get_object_or_404(Employee, pk=self.kwargs.get('employee_id'))
        return initial

    def get_context_data(self, **kwargs):
        #print('kwargs(views) = ', self.kwargs['employee_id'], type(self.kwargs['employee_id']))
        context = super().get_context_data(**kwargs)

        kwargs['user'] = self.request.user

        employee = Employee.objects.get(pk=int(self.kwargs['employee_id']))
        context['employee'] = employee
        context['employees'] = Employee.objects.all()
        context['vacations'] = Vacation.objects.all()
        context['departments'] = Department.objects.all()
        context['vacation_days_by_month'] = employee.department.vacation_days_by_month

        return context


class VacationDeleteView(DeleteView):
    template_name = 'vacations/delete_vacation.html'
    model = Vacation
    success_url = reverse_lazy('vacations:index')
    #success_url = reverse_lazy('vacations:details', kwargs={'employee_id': instance.id})

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get(self, *args, **kwargs):
        user = self.request.user
        if not user.is_staff:
            if not user.employees_permission_level >= EDIT:  # ++ if not HR
                messages.warning(self.request, 'Недостаточно прав для удаления отпусков')
                return redirect('vacations:details', kwargs['employee_id'])
        return super(VacationDeleteView, self).get(args, kwargs)

    def post(self, *args, **kwargs):
        user = self.request.user
        if not user.is_staff:
            if not user.employees_permission_level >= EDIT:  # ++ if not HR
                messages.warning(self.request, 'Недостаточно прав для удаления отпусков')
                return redirect('vacations:details', kwargs['employee_id'])
        return super(VacationDeleteView, self).post(args, kwargs)

    #def get_success_url(self):
    #    return reverse_lazy('vacations:details', kwargs={'employee_id': self.kwargs['employee_id']})


@login_required
def by_department(request, department_id):
    employees = Employee.objects.filter(department=department_id)
    vacations = Vacation.objects.all()
    departments = Department.objects.all()
    current_department = Department.objects.get(pk=department_id)
    vacation_days_by_month = current_department.vacation_days_by_month

    user = request.user

    #current_department.test_vacation_days()

    if not user.is_staff:
        if not (user.employees_permission_level >= VIEW or (user.bound_employee.department.pk == department_id and user.is_department_manager)):
            #messages.warning(request, 'Недостаточно прав для доступа к странице')
            return redirect('vacations:details', user.bound_employee.pk)



    context = {'employees': employees, 'departments': departments, 'vacations': vacations,
               'current_department': current_department, 'vacation_days_by_month': vacation_days_by_month}
    return render(request, 'vacations/by_department.html', context)


@login_required
def recalculate_department(request, department_id):
    employees = Employee.objects.filter(department=department_id)
    vacations = Vacation.objects.all()
    departments = Department.objects.all()
    current_department = Department.objects.get(pk=department_id)
    vacation_days_by_month = current_department.vacation_days_by_month

    user = request.user

    if not user.is_staff:
        if not (user.employees_permission_level >= VIEW or (user.bound_employee.department.pk == department_id and user.is_department_manager)):
            #messages.warning(request, 'Недостаточно прав для доступа к странице')
            return redirect('vacations:details', user.bound_employee.pk)

    employee_days_coef = employees.count() / 12
    current_year = date.today().year
    for month in range(1, 13):
        vacation_days_by_month[month-1] = round(employee_days_coef * monthrange(current_year, month)[1])

    for employee in employees:
        employee.reset_rating()
        logger.debug(employee.rating)

    for vacation in vacations:
        if vacation.employee in employees:
            current_department.change_vacation_days(vacation.start, vacation.end)
            vacation.change_values()

    return redirect('vacations:by_department', department_id)

'''
@login_required
def details(request, employee_id):
    current_employee = Employee.objects.get(pk=employee_id)
    employees = Employee.objects.all()
    vacations = Vacation.objects.all()
    departments = Department.objects.all()
    context = {'employees': employees, 'vacations': vacations,
               'departments': departments, 'employee': current_employee}
    return render(request, 'vacations/details.html', context)
'''


@login_required
def index(request):
    employees = Employee.objects.all()
    vacations = Vacation.objects.all()
    departments = Department.objects.all()

    user = request.user


    if not (user.employees_permission_level >= VIEW or user.is_staff):  # ++ if not HR
        #messages.warning(request, 'Недостаточно прав для доступа к странице')
        return redirect('vacations:by_department', user.bound_employee.department.pk)

    context = {'employees': employees, 'vacations': vacations, 'departments': departments}
    return render(request, 'vacations/index.html', context)


def success(request):
    return render(request, 'vacations/success.html')


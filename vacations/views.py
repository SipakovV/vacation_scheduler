import logging

from django.shortcuts import render, get_object_or_404, redirect
from django.utils.decorators import method_decorator
from django.contrib import messages
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy, reverse

from .models import Employee, Department, Vacation
from .forms import VacationForm, EmployeeForm, DepartmentForm

from django.contrib.auth.decorators import login_required

logger = logging.getLogger(__name__)


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
            if not (False):  # ++ if not HR
                messages.warning(self.request, 'Недостаточно прав для добавления отдела')
                return redirect('vacations:index')
        return super(DepartmentCreateView, self).get(args, kwargs)


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
            if not (False):  # ++ if not HR
                messages.warning(self.request, 'Недостаточно прав для удаления отдела')
                return redirect('vacations:index')
        return super(DepartmentDeleteView, self).get(args, kwargs)


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
            if not (False):  # ++ if not HR
                messages.warning(self.request, 'Недостаточно прав для добавления сотрудников')
                return redirect('vacations:index')
        return super(EmployeeCreateView, self).get(args, kwargs)


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
            if not (False):  # ++ if not HR
                messages.warning(self.request, 'Недостаточно прав для редактирования данных сотрудников')
                return redirect('vacations:details', kwargs['pk'])
        return super(EmployeeUpdateView, self).get(args, kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['employee'] = Employee.objects.get(pk=int(self.kwargs['pk']))
        return context


class EmployeeDeleteView(DeleteView):
    template_name = 'vacations/delete_employee.html'
    model = Employee

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get(self, *args, **kwargs):
        user = self.request.user
        if not user.is_staff:
            if not (False):  # ++ if not HR
                messages.warning(self.request, 'Недостаточно прав для удаления сотрудников')
                return redirect('vacations:details', kwargs['employee_id'])
        return super(EmployeeDeleteView, self).get(args, kwargs)


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
            if not (False or user.bound_employee.pk == self.kwargs['employee_id'] or user.is_department_manager):  # ++ if not HR
                messages.warning(self.request, 'Недостаточно прав для доступа к странице')
                return redirect('vacations:by_department', user.bound_employee.department.pk)
        return super(VacationCreateView, self).get(args, kwargs)

    '''
    def post(self, *args, **kwargs):
        user = self.request.user
        if not user.is_staff:
            if not user.is_department_manager:
                messages.warning(self.request, 'Недостаточно прав для добавления отпусков')
                return redirect('vacations:by_department', user.bound_employee.department.pk)
        return super(VacationCreateView, self).post(args, kwargs)
    '''

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

        context['employees'] = Employee.objects.all()
        context['vacations'] = Vacation.objects.all()
        context['departments'] = Department.objects.all()

        context['employee'] = Employee.objects.get(pk=int(self.kwargs['employee_id']))
        empl = self.kwargs['employee_id']
        #print('CreateView.initial = ', self.initial)

        return context


@login_required
def by_department(request, department_id):
    employees = Employee.objects.filter(department=department_id)
    vacations = Vacation.objects.all()
    departments = Department.objects.all()
    current_department = Department.objects.get(pk=department_id)

    user = request.user

    if not (user.is_staff or user.bound_employee.department.pk == department_id):  # ++ if not HR
        messages.warning(request, 'Недостаточно прав для доступа к странице')
        return redirect('vacations:by_department', user.bound_employee.department.pk)

    context = {'employees': employees, 'departments': departments, 'vacations': vacations,
               'current_department': current_department}
    return render(request, 'vacations/by_department.html', context)


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

    if not (False or user.is_staff):  # ++ if not HR
        #messages.warning(request, 'Недостаточно прав для доступа к странице')
        return redirect('vacations:by_department', user.bound_employee.department.pk)

    context = {'employees': employees, 'vacations': vacations, 'departments': departments}
    return render(request, 'vacations/index.html', context)


def success(request):
    return render(request, 'vacations/success.html')


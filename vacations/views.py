from django.shortcuts import render, get_object_or_404

from django.views.generic.edit import CreateView, UpdateView
from django.urls import reverse_lazy
from pyatspi import setTimeout

from .models import Employee, Department, Vacation
from .forms import VacationForm, EmployeeForm, DepartmentForm


# Create your views here.


class DepartmentCreateView(CreateView):
    template_name = 'vacations/add_department.html'
    form_class = DepartmentForm
    success_url = reverse_lazy('index')


class EmployeeCreateView(CreateView):
    template_name = 'vacations/add_employee.html'
    form_class = EmployeeForm
    success_url = reverse_lazy('index')


class EmployeeUpdateView(UpdateView):
    template_name = 'vacations/edit_employee.html'
    #form_class = EmployeeForm
    success_url = reverse_lazy('index')
    model = Employee
    fields = ('department', 'replaces', 'entry_date', 'vacation_days')
    template_name_suffix = '_update_form'
    #employee = get_object_or_404(pk=kwargs.get('employee_id')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['employee'] = Employee.objects.get(pk=int(self.kwargs['pk']))
        return context
    #def get_success_url(self):
    #    return reverse_lazy('details', kwargs={'employee_id': employee_id})


class VacationCreateView(CreateView):
    template_name = 'vacations/details.html'
    form_class = VacationForm
    # success_url = reverse_lazy('add')
    employee_id = '0'

    def get_success_url(self):
        employee_id = self.kwargs['employee_id']
        print('get_success_url employee_id = ', employee_id)
        return reverse_lazy('details', kwargs={'employee_id': employee_id})

    def get_initial(self):
        employee = get_object_or_404(Employee, pk=self.kwargs.get('employee_id'))
        return {
            'employee': employee,
        }

    def get_context_data(self, **kwargs):
        print('kwargs(views) = ', self.kwargs['employee_id'], type(self.kwargs['employee_id']))
        context = super().get_context_data(**kwargs)
        context['employees'] = Employee.objects.all()
        context['vacations'] = Vacation.objects.all()
        context['departments'] = Department.objects.all()

        context['employee'] = Employee.objects.get(pk=int(self.kwargs['employee_id']))
        empl = self.kwargs['employee_id']
        # self.initial = {'employee': Employee.objects.get(pk=int(empl))}
        print('CreateView.initial = ', self.initial)

        return context


def by_department(request, department_id):
    employees = Employee.objects.filter(department=department_id)
    vacations = Vacation.objects.all()
    departments = Department.objects.all()
    current_department = Department.objects.get(pk=department_id)
    context = {'employees': employees, 'departments': departments, 'vacations': vacations,
               'current_department': current_department}
    return render(request, 'vacations/by_department.html', context)


def details(request, employee_id):
    current_employee = Employee.objects.get(pk=employee_id)
    employees = Employee.objects.all()
    vacations = Vacation.objects.all()
    departments = Department.objects.all()
    context = {'employees': employees, 'vacations': vacations,
               'departments': departments, 'employee': current_employee}
    return render(request, 'vacations/details.html', context)


def index(request):
    employees = Employee.objects.all()
    vacations = Vacation.objects.all()
    departments = Department.objects.all()

    context = {'employees': employees, 'vacations': vacations, 'departments': departments}
    return render(request, 'vacations/index.html', context)


def success(request):
    return render(request, 'vacations/success.html')

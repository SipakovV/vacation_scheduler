from django.db.models.functions import ExtractMonth, Extract
from django.shortcuts import render
from django.views.decorators.clickjacking import xframe_options_exempt

from django.views.generic.edit import CreateView
from django.urls import reverse_lazy
from pyatspi import setTimeout

from .models import Employee, Department, Vacation
from .forms import VacationForm

# Create your views here.


class VacationCreateView(CreateView):
    template_name = 'vacations/add.html'
    form_class = VacationForm
    success_url = reverse_lazy('add')
    #success_url = '/vacations/add1.html'

    #def form_valid(self, form):
    #    form.employee = Employee.objects.get(pk=self.kwargs['empl'])
    #    return super().form_valid(form)

    def get_context_data(self, **kwargs):
        print('kwargs(views) = ', self.kwargs['empl'])
        context = super().get_context_data(**kwargs)
        context['employees'] = Employee.objects.all()
        #empl = Employee.objects.get(pk=self.kwargs['empl'])

        return context
    '''
    def form_valid(self, form):
        # This method is called when valid form data has been POSTed.
        # It should return an HttpResponse.
        print('form_valid')
        return super().form_valid(form)
    
    def form_invalid(self, form):
        print('form_invalid')
        return super().form_invalid(form)
    
    def POST(self):
        print('POST() called')
        try:
            super.POST(self)
        except ValidationError:
            print('ValidationError exception!!!')
    '''


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

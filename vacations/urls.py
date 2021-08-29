from django.urls import path, re_path
from django.views.generic import TemplateView

from .views import index, by_department, details, VacationCreateView, EmployeeCreateView, EmployeeUpdateView, success, DepartmentCreateView

urlpatterns = [
    path('', index, name='index'),
    path('department/add/', DepartmentCreateView.as_view(), name='add_department'),
    path('department/<int:department_id>/', by_department, name='by_department'),
    path('employee/add/', EmployeeCreateView.as_view(), name='add_employee'),
    path('employee/<int:pk>/edit', EmployeeUpdateView.as_view(), name='employee_update_form'),
    path('employee/<int:employee_id>/', VacationCreateView.as_view(), name='details'),

    #path('success/', success, name='success'),
]

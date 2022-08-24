
from django.urls import path, include
from django.views.generic.base import RedirectView

from .views import index, by_department, VacationCreateView, EmployeeCreateView, EmployeeUpdateView, success, \
    DepartmentCreateView, EmployeeDeleteView, DepartmentDeleteView, VacationDeleteView, recalculate_department, \
    export_t7_department, export_t7_all

app_name = 'vacations'

urlpatterns = [

    path('', index, name='index'),
    path('export_t7/', export_t7_all, name='export_t7_all'),
    path('department/', RedirectView.as_view(pattern_name='vacations:index', permanent=False), name='index_redirect'),
    path('department/add/', DepartmentCreateView.as_view(), name='add_department'),
    path('department/<int:pk>/delete/', DepartmentDeleteView.as_view(), name='department_delete_form'),
    path('department/<int:department_id>/export_t7', export_t7_department, name='export_t7_department'),
    path('department/<int:department_id>/recalculate', recalculate_department, name='recalculate_department'),
    path('department/<int:department_id>/', by_department, name='by_department'),
    path('employee/add/', EmployeeCreateView.as_view(), name='add_employee'),
    path('employee/<int:pk>/edit/', EmployeeUpdateView.as_view(), name='employee_update_form'),
    path('employee/<int:pk>/delete/',  EmployeeDeleteView.as_view(), name='employee_delete_form'),
    path('employee/<int:employee_id>/', VacationCreateView.as_view(), name='details'),
    path('vacation/<int:pk>/delete/', VacationDeleteView.as_view(), name='vacation_delete_form'),


]

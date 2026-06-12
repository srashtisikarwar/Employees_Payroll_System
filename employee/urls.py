from django.urls import path
from . import views

app_name = 'employee'

urlpatterns = [
    path('', views.employee_list, name='employee_list'),
    path('add/', views.add_employee, name='add_employee'),
    path('<int:employee_id>/', views.employee_detail, name='employee_detail'),
    path('<int:employee_id>/edit/', views.edit_employee, name='edit_employee'),
    path('<int:employee_id>/delete/', views.delete_employee, name='delete_employee'),
    path('salary-prediction/', views.salary_prediction, name='salary_prediction'),
    path('salary-records/', views.salary_records, name='salary_records'),
    path('chatbot/', views.chatbot, name='chatbot'),
    path('attendance/', views.mark_attendance, name='mark_attendance'),
    path('report/', views.generate_report, name='generate_report'),
    path('download-pdf/', views.download_pdf_report, name='download_pdf'),
    path('process-payroll/', views.process_payroll, name='process_payroll'),
    path('payroll-records/', views.payroll_list, name='payroll_list'),
    path("dashboard/", views.dashboard, name='dashboard'),
    path('redirect/', views.role_redirect, name='role_redirect'),

    path('employee-dashboard/',views.employee_dashboard,name='employee_dashboard'),
    path('my-payroll/', views.my_payroll, name='my_payroll'),
    path('my-profile/', views.my_profile, name='my_profile'),
    path('my-attendance/', views.my_attendance, name='my_attendance'),
    path('my-salary/', views.my_salary, name='my_salary'),
    path('logout/', views.user_logout, name='logout'),
   
]
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
    path('payroll/', views.payroll_list, name='payroll_list'),
    
]
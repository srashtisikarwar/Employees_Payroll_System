from django.db import models

# Create your models here.
class Employee(models.Model):
    emp_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    designation = models.CharField(max_length=100)
    department = models.CharField(max_length=100)
    joining_date = models.DateField()
    basic_salary = models.DecimalField(max_digits=10, decimal_places=2)
    email = models.EmailField()
    phone = models.CharField(max_length=15,default='0000000000')

    def __str__(self):
        return self.name
    
class Attendance(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    date = models.DateField()
    status = models.CharField(max_length=10, choices=[
        ('present', 'Present'),
        ('absent', 'Absent'),
        ('leave', 'On Leave')
    ], default='present')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['employee', 'date']

    def __str__(self):
        return f"{self.employee.name} - {self.date} - {self.status}"
    
class Activity(models.Model):
    ACTION_CHOICES = [
        ('added', 'New Employee Added'),
        ('salary', 'Salary Processed'),
        ('leave', 'Leave Approved'),
    ]

    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    action_type = models.CharField(max_length=50, choices=ACTION_CHOICES)
    description = models.TextField(blank=True, null=True)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.employee.name} - {self.get_action_type_display()}"
    
class Payroll(models.Model):
        employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
        month = models.CharField(max_length=20)
        year = models.IntegerField()
        basic = models.DecimalField(max_digits=10, decimal_places=2)
        hra = models.DecimalField(max_digits=10, decimal_places=2)
        bonus = models.DecimalField(max_digits=10, decimal_places=2)
        deductions = models.DecimalField(max_digits=10, decimal_places=2)
        net_salary = models.DecimalField(max_digits=10, decimal_places=2)
        created_at = models.DateTimeField(auto_now_add=True)
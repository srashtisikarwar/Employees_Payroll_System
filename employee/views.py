import json
from urllib import request
from django.http import JsonResponse
from django.shortcuts import render,redirect
from datetime import date
from decimal import Decimal
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from django.contrib import messages
from datetime import datetime


from django.http import HttpResponseRedirect,HttpResponse
from django.urls import reverse
from django.db.models import Sum
from django.utils import timezone
from .models import Employee
from .models import Activity
from .models import Attendance
from .models import Payroll


def ask_ai(question):
    q = question.lower()
    today = timezone.now().date()
    employees = Employee.objects.all()

    # ================================
    # ✅ 1. HOW MANY (TOP PRIORITY)
    # ================================
    if "how many" in q:

        # Employee attendance history
        for emp in employees:
            if emp.name.lower() in q:

                if "present" in q:
                    count = Attendance.objects.filter(employee=emp, status='present').count()
                    return f"{emp.name} was present for {count} days."

                elif "absent" in q:
                    count = Attendance.objects.filter(employee=emp, status='absent').count()
                    return f"{emp.name} was absent for {count} days."

                elif "leave" in q:
                    count = Attendance.objects.filter(employee=emp, status='leave').count()
                    return f"{emp.name} was on leave for {count} days."

        # Department count
        for dept in Employee.objects.values_list('department', flat=True).distinct():
            if dept.lower() in q:
                count = Employee.objects.filter(department__iexact=dept).count()
                return f"👨‍💻 {count} employees are working in the {dept} department."

        # Total employees
        if "employee" in q:
            total = employees.count()
            return f"There are {total} employees in the company."

    # ================================
    # ✅ 2. EMPLOYEE TODAY STATUS
    # ================================
    for emp in employees:
        if emp.name.lower() in q and any(word in q for word in ["present", "absent", "leave"]):

            record = Attendance.objects.filter(employee=emp, date=today).first()

            if not record:
                return f"No attendance marked for {emp.name} today."

            if record.status == 'present':
                return f"Yes, {emp.name} is present today."
            elif record.status == 'absent':
                return f"No, {emp.name} is absent today."
            elif record.status == 'leave':
                return f"{emp.name} is on leave today."

    # ================================
    # ✅ 3. TODAY ATTENDANCE (LIST OR COUNT)
    # ================================
    if "present" in q:
        names = list(Attendance.objects.filter(date=today, status='present')
                     .values_list('employee__name', flat=True))

        if any(word in q for word in ["who", "name", "list"]):
            return f"✅ Present employees:\n" + "\n".join(names) if names else "No employees are present today."
        return f"{len(names)} employees are present today."

    elif "absent" in q:
        names = list(Attendance.objects.filter(date=today, status='absent')
                     .values_list('employee__name', flat=True))

        if any(word in q for word in ["who", "name", "list"]):
            return f"❌ Absent employees:\n" + "\n".join(names) if names else "No employees are absent today."
        return f"{len(names)} employees are absent today."

    elif "leave" in q:
        names = list(Attendance.objects.filter(date=today, status='leave')
                     .values_list('employee__name', flat=True))

        if any(word in q for word in ["who", "name", "list"]):
            return f"🌴 Employees on leave:\n" + "\n".join(names) if names else "No employees are on leave today."
        return f"{len(names)} employees are on leave today."

    # ================================
    # ✅ 4. ALL EMPLOYEES LIST
    # ================================
    if "all employees" in q or "list of employees" in q:
        if employees.exists():
            names = [emp.name for emp in employees]
            return "👨‍💼 All Employees:\n" + "\n".join(names)
        return "No employees found."

    # ================================
    # ✅ 5. EMPLOYEE LIST BY DEPARTMENT
    # ================================
    if any(word in q for word in ["list", "show", "give"]):
        for dept in Employee.objects.values_list('department', flat=True).distinct():
            if dept.lower() in q:
                emp_list = Employee.objects.filter(department__iexact=dept)

                if emp_list.exists():
                    names = [emp.name for emp in emp_list]
                    return f"📁 Employees in {dept} department:\n" + "\n".join(names)

                return f"No employees found in {dept} department."

    # ================================
    # ✅ 6. PAYROLL
    # ================================
    if ("salary" in q and "total" in q) or ("payroll" in q):
        total = Employee.objects.aggregate(Sum('basic_salary'))['basic_salary__sum'] or 0
        return f"💰 Total payroll is ₹{total}"

    # ================================
    # ✅ 7. INDIVIDUAL SALARY
    # ================================
    if "salary" in q:
        for emp in employees:
            if emp.name.lower() in q:
                return f"{emp.name}'s salary is ₹{emp.basic_salary}"
        return "Please mention a valid employee name."

    # ================================
    # ✅ 8. DEPARTMENTS
    # ================================
    if "department" in q:
        departments = Employee.objects.values_list('department', flat=True).distinct()
        return "🏢 Departments:\n" + "\n".join(departments)

    # ================================
    # ✅ 9. JOINING DATE
    # ================================
    if "join" in q:
        for emp in employees:
            if emp.name.lower() in q:
                return f"{emp.name} joined on {emp.joining_date}"
        return "Please mention employee name."

    # ================================
    return "Try asking about attendance, salary, employees, departments, or joining date."
def chatbot(request):
    # 🟢 Handle AJAX (fetch request)
    if request.method == 'POST':
        question = request.POST.get('question', '').strip()

        if not question:
            return JsonResponse({
                'answer': "Please ask something."
            })

        answer = ask_ai(question)

        return JsonResponse({
            'answer': answer
        })

    # 🟢 First page load
    return render(request, 'employee/chatbot.html')
def dashboard(request):
    today = timezone.now().date()
    total_employees = Employee.objects.count()
    present_today = Attendance.objects.filter(date=today, status='present').count()
    total_salary = Employee.objects.aggregate(Sum('basic_salary'))['basic_salary__sum'] or 0
    total_departments = Employee.objects.values('department').distinct().count()

    # Get recent activities from database
    recent_activities = Activity.objects.select_related('employee').order_by('-date')[:10]
    # Format activities for template
    activities_data = []
    for activity in recent_activities:
        activities_data.append({
            'employee': activity.employee.name,
            'action': activity.get_action_type_display(),
            'date': activity.date.strftime('%Y-%m-%d')
        })

    return render(request, 'dashboard.html', {
        'total_employees': total_employees,
        'present_today': present_today,
        'total_salary': total_salary,
        'total_departments': total_departments,
        'activities': recent_activities
    })




# Create your views here
def employee_list(request):
    employees = Employee.objects.all()
    return render(request, 'employee/employee_list.html', {'employees': employees})

def add_employee(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        designation = request.POST.get('designation')
        department = request.POST.get('department')
        joining_date = request.POST.get('joining_date')
        basic_salary = request.POST.get('basic_salary')
        email = request.POST.get('email')
        phone = request.POST.get('phone', '0000000000')

        # Save employee
        new_employee = Employee.objects.create(
            name=name,
            designation=designation,
            department=department,
            joining_date=joining_date,
            basic_salary=basic_salary,
            email=email,
            phone=phone
        )

        # ----------- SAVE REAL ACTIVITY HERE -------------
        Activity.objects.create(
            employee=new_employee,
            action_type='added',  # from choices
            description='A new employee was added to the system.'
        )
        # --------------------------------------------------

        return HttpResponseRedirect(reverse('employee:employee_list'))

    return render(request, 'employee/add_employee.html')

def process_payroll(request):
    employees = Employee.objects.all()
    today = datetime.now()

    for emp in employees:
        basic = emp.basic_salary

        # ✅ HRA = 20% of basic
        hra = basic * 0.20

        # ✅ Bonus = 10%
        bonus = basic * 0.10

        # ✅ Attendance-based deduction
        total_days = 30
        present_days = Attendance.objects.filter(
            employee=emp,
            status='present'
        ).count()

        absent_days = total_days - present_days

        deduction_per_day = basic / total_days
        deductions = absent_days * deduction_per_day

        # ✅ Final Salary
        net_salary = basic + hra + bonus - deductions

        # ✅ SAVE to Payroll table
        Payroll.objects.create(
            employee=emp,
            month=today.strftime("%B"),
            year=today.year,
            basic=basic,
            hra=hra,
            bonus=bonus,
            deductions=deductions,
            net_salary=net_salary
        )

        # ✅ Save activity
        Activity.objects.create(
            employee=emp,
            action_type='salary',
            description=f'Payroll processed. Net Salary ₹{round(net_salary,2)}'
        )

    messages.success(request, "✅ Payroll processed successfully for all employees!")
    return redirect('employee:dashboard')

def payroll_list(request):
    records = Payroll.objects.select_related('employee').order_by('-created_at')

    return render(request, 'employee/payroll_list.html', {
        'records': records
    })

def edit_employee(request, employee_id):
    employee = Employee.objects.get(emp_id=employee_id)

    if request.method == 'POST':
        employee.name = request.POST.get('name')
        employee.designation = request.POST.get('designation')
        employee.department = request.POST.get('department')
        employee.joining_date = request.POST.get('joining_date')
        employee.basic_salary = request.POST.get('basic_salary')
        employee.email = request.POST.get('email')
        employee.phone = request.POST.get('phone', '0000000000')

        employee.save()

    return render(request, 'employee/edit_employee.html', {'employee': employee})

def delete_employee(request, employee_id):
    employee = Employee.objects.get(emp_id=employee_id)
    employee.delete()
    employees = Employee.objects.all()
    return HttpResponseRedirect(reverse('employee:employee_list'))

def employee_detail(request, employee_id):
    employee = Employee.objects.get(emp_id=employee_id)
    return render(request, 'employee/employee_detail.html', {'employee': employee})


def salary_records(request):
    employees = Employee.objects.order_by('name')
    total_salary = employees.aggregate(Sum('basic_salary'))['basic_salary__sum'] or 0
    return render(request, 'employee/salary_records.html', {
        'employees': employees,
        'total_salary': total_salary,
    })


def mark_attendance(request):
    today = timezone.now().date()
    employees = Employee.objects.all()
    message = None

    # Add attendance_today to each employee
    for employee in employees:
        try:
            employee.attendance_today = Attendance.objects.get(employee=employee, date=today)
        except Attendance.DoesNotExist:
            employee.attendance_today = None

    if request.method == 'POST':
        attendance_count = 0
        for employee in employees:
            status = request.POST.get(f'status_{employee.emp_id}')
            if status:
                attendance, created = Attendance.objects.get_or_create(
                    employee=employee,
                    date=today,
                    defaults={'status': status}
                )
                if not created:
                    attendance.status = status
                    attendance.save()
                attendance_count += 1

        message = f"Attendance marked for {attendance_count} employees on {today.strftime('%B %d, %Y')}."

    return render(request, 'employee/mark_attendance.html', {
        'employees': employees,
        'message': message,
        'today': today
    })


def salary_prediction(request):
    employees = Employee.objects.all()
    prediction = None
    selected_employee_name = None
    chart_labels = [employee.name for employee in employees]
    chart_data = [float(employee.basic_salary) for employee in employees]
    chart_title = 'Current Employee Salary Data'
    candidate_name_input = ''
    candidate_salary_input = ''
    candidate_experience_input = ''

    if request.method == 'POST':
        employee_id = request.POST.get('employee')
        candidate_name_input = request.POST.get('candidate_name', '').strip()
        candidate_salary_input = request.POST.get('candidate_salary', '').strip()
        candidate_experience_input = request.POST.get('candidate_experience', '').strip()

        if employee_id:
            employee = Employee.objects.get(emp_id=employee_id)
            selected_employee_name = employee.name
            experience_days = (date.today() - employee.joining_date).days
            experience_years = max(0, experience_days // 365)
            experience_factor = Decimal('0.05') * Decimal(experience_years)
            predicted_salary = employee.basic_salary * (Decimal('1.0') + experience_factor)
            prediction = {
                'selected': selected_employee_name,
                'current_salary': float(employee.basic_salary),
                'predicted_salary': round(predicted_salary, 2),
                'experience_years': experience_years,
                'confidence': 85,
                'factors': f'Based on {experience_years} years of experience'
            }
            chart_labels = ['Current Salary', 'Predicted Salary']
            chart_data = [float(employee.basic_salary), float(predicted_salary)]
            chart_title = f'Salary Prediction for {selected_employee_name}'
        elif candidate_salary_input and candidate_experience_input:
            try:
                normalized_salary = candidate_salary_input.replace(',', '').replace(' ', '')
                base_salary = Decimal(normalized_salary)
                experience_years = max(0, int(candidate_experience_input))
                predicted_salary = base_salary * (Decimal('1.0') + Decimal('0.05') * Decimal(experience_years))
                prediction = {
                    'selected': candidate_name_input or 'New Candidate',
                    'current_salary': float(base_salary),
                    'predicted_salary': round(predicted_salary, 2),
                    'experience_years': experience_years,
                    'confidence': 80,
                    'factors': f'Based on {experience_years} years of prior experience'
                }
                chart_labels = ['Base Salary', 'Predicted Salary']
                chart_data = [float(base_salary), float(predicted_salary)]
                chart_title = f'Salary Prediction for {prediction["selected"]}'
            except Exception:
                prediction = {
                    'error': 'Please enter a valid salary and experience value.'
                }

    return render(request, 'employee/salary_prediction.html', {
        'employees': employees,
        'prediction': prediction,
        'selected_employee_name': selected_employee_name,
        'candidate_name_input': candidate_name_input,
        'candidate_salary_input': candidate_salary_input,
        'candidate_experience_input': candidate_experience_input,
        'chart_labels_json': json.dumps(chart_labels),
        'chart_data_json': json.dumps(chart_data),
        'chart_title_json': json.dumps(chart_title)
    })
def generate_report(request):
    employees = Employee.objects.all()
    today = timezone.now().date()

    total_employees = employees.count()
    total_salary = employees.aggregate(Sum('basic_salary'))['basic_salary__sum'] or 0
    present = Attendance.objects.filter(date=today, status='present').count()
    absent = Attendance.objects.filter(date=today, status='absent').count()

    return render(request, 'employee/report.html', {
        'employees': employees,
        'total_employees': total_employees,
        'total_salary': total_salary,
        'present': present,
        'absent': absent,
        'today': today
    })

def download_pdf_report(request):

    report_type = request.GET.get("type", "daily")  # daily or monthly
    today = timezone.now().date()

    # PDF response
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="HR_Report.pdf"'

    p = canvas.Canvas(response, pagesize=A4)
    width, height = A4

    y = height - 50

    # ===================== TITLE =====================
    p.setFont("Helvetica-Bold", 18)

    if report_type == "monthly":
        p.drawString(180, y, "MONTHLY HR REPORT")
    else:
        p.drawString(190, y, "DAILY HR REPORT")

    y -= 30

    p.setFont("Helvetica", 11)
    p.drawString(220, y, f"Date: {today}")
    y -= 40

    # ===================== DATA LOGIC =====================
    if report_type == "monthly":
        start_date = today.replace(day=1)

        present = Attendance.objects.filter(
            date__gte=start_date,
            date__lte=today,
            status='present'
        ).count()

        absent = Attendance.objects.filter(
            date__gte=start_date,
            date__lte=today,
            status='absent'
        ).count()

    else:
        present = Attendance.objects.filter(date=today, status='present').count()
        absent = Attendance.objects.filter(date=today, status='absent').count()

    total_employees = Employee.objects.count()
    total_salary = Employee.objects.aggregate(
        Sum('basic_salary')
    )['basic_salary__sum'] or 0

    # ===================== STATS SECTION =====================
    p.setFont("Helvetica-Bold", 12)
    p.drawString(50, y, f"Total Employees: {total_employees}")
    y -= 20
    p.drawString(50, y, f"Present: {present}")
    y -= 20
    p.drawString(50, y, f"Absent: {absent}")
    y -= 20
    p.drawString(50, y, f"Total Salary: ₹{total_salary}")

    y -= 40

    # ===================== TABLE HEADER =====================
    p.setFont("Helvetica-Bold", 12)
    p.drawString(50, y, "Name")
    p.drawString(220, y, "Department")
    p.drawString(400, y, "Salary")

    y -= 20

    # ===================== TABLE DATA =====================
    p.setFont("Helvetica", 10)
    employees = Employee.objects.all()

    for emp in employees:
        p.drawString(50, y, str(emp.name))
        p.drawString(220, y, str(emp.department))
        p.drawString(400, y, f"₹{emp.basic_salary}")

        y -= 18

        if y < 60:
            p.showPage()
            y = height - 50

    p.save()
    return response
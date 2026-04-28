from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Student, Report


def home(request):
    return redirect("register")


def register(request):
    if request.method == "POST":
        student_id = request.POST.get("student_id", "").strip()
        name = request.POST.get("name", "").strip()
        password = request.POST.get("password", "").strip()
        english = request.POST.get("english_grade", "").strip()
        math = request.POST.get("math_grade", "").strip()
        science = request.POST.get("science_grade", "").strip()

        if not all([student_id, name, password, english, math, science]):
            messages.error(request, "All fields are required!")
            students = Student.objects.all().order_by("-date_registered")
            return render(request, "portal/register.html", {"students": students})

        try:
            english = float(english)
            math = float(math)
            science = float(science)
        except ValueError:
            messages.error(request, "Grades must be valid numbers!")
            students = Student.objects.all().order_by("-date_registered")
            return render(request, "portal/register.html", {"students": students})

        for grade in [english, math, science]:
            if not (0 <= grade <= 100):
                messages.error(request, "Grades must be between 0 and 100!")
                students = Student.objects.all().order_by("-date_registered")
                return render(request, "portal/register.html", {"students": students})

        if Student.objects.filter(student_id=student_id).exists():
            messages.error(request, f"Student ID '{student_id}' already exists!")
            students = Student.objects.all().order_by("-date_registered")
            return render(request, "portal/register.html", {"students": students})

        Student.objects.create(
            student_id=student_id,
            name=name,
            password=password,
            english_grade=english,
            math_grade=math,
            science_grade=science,
        )
        messages.success(request, f"Student '{name}' registered successfully!")
        return redirect("register")

    students = Student.objects.all().order_by("-date_registered")
    return render(request, "portal/register.html", {"students": students})


def students_list(request):
    students = Student.objects.all().order_by("-date_registered")
    return render(request, "portal/students_list.html", {"students": students})


def reports(request):
    all_reports = Report.objects.all().select_related("student").order_by("-date_sent")
    return render(request, "portal/reports.html", {"reports": all_reports})

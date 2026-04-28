"""
PT4 Setup Script
Run this ONCE to create the entire project structure.
Usage: python setup_pt4.py
"""

import os
import subprocess
import sys

BASE = os.path.dirname(os.path.abspath(__file__))
PROJECT = os.path.join(BASE, "pt4_portal")

def write(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"  Created: {os.path.relpath(path, BASE)}")

def touch(path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    open(path, "a").close()

print("\n========================================")
print("  PT4 Student Portal - Setup Script")
print("========================================\n")

# ── manage.py ────────────────────────────────────────────────
write(os.path.join(PROJECT, "manage.py"), '''#!/usr/bin/env python
import os
import sys

def main():
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "pt4_portal.settings")
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError("Django not installed. Run: pip install django") from exc
    execute_from_command_line(sys.argv)

if __name__ == "__main__":
    main()
''')

# ── pt4_portal/__init__.py ───────────────────────────────────
write(os.path.join(PROJECT, "pt4_portal", "__init__.py"), "")

# ── pt4_portal/settings.py ───────────────────────────────────
write(os.path.join(PROJECT, "pt4_portal", "settings.py"), '''from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = "pt4-simple-secret-key-change-in-production"
DEBUG = True
ALLOWED_HOSTS = ["*"]

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "portal",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "pt4_portal.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "pt4_portal.wsgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "PT4_DB_Student.sqlite3",
    }
}

LANGUAGE_CODE = "en-us"
TIME_ZONE = "Asia/Manila"
USE_I18N = True
USE_TZ = True
STATIC_URL = "static/"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
''')

# ── pt4_portal/urls.py ───────────────────────────────────────
write(os.path.join(PROJECT, "pt4_portal", "urls.py"), '''from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("portal.urls")),
]
''')

# ── pt4_portal/wsgi.py ───────────────────────────────────────
write(os.path.join(PROJECT, "pt4_portal", "wsgi.py"), '''import os
from django.core.wsgi import get_wsgi_application
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "pt4_portal.settings")
application = get_wsgi_application()
''')

# ── portal/__init__.py ───────────────────────────────────────
write(os.path.join(PROJECT, "portal", "__init__.py"), "")

# ── portal/apps.py ───────────────────────────────────────────
write(os.path.join(PROJECT, "portal", "apps.py"), '''from django.apps import AppConfig

class PortalConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "portal"
''')

# ── portal/models.py ─────────────────────────────────────────
write(os.path.join(PROJECT, "portal", "models.py"), '''from django.db import models


class Student(models.Model):
    student_id = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=100)
    password = models.CharField(max_length=100)
    english_grade = models.FloatField(default=0)
    math_grade = models.FloatField(default=0)
    science_grade = models.FloatField(default=0)
    date_registered = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student_id} - {self.name}"


class Report(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="reports")
    message = models.TextField()
    date_sent = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Report from {self.student.name} on {self.date_sent.strftime(\'%Y-%m-%d %H:%M\')}"
''')

# ── portal/views.py ──────────────────────────────────────────
write(os.path.join(PROJECT, "portal", "views.py"), '''from django.shortcuts import render, redirect
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
            messages.error(request, f"Student ID \'{student_id}\' already exists!")
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
        messages.success(request, f"Student \'{name}\' registered successfully!")
        return redirect("register")

    students = Student.objects.all().order_by("-date_registered")
    return render(request, "portal/register.html", {"students": students})


def students_list(request):
    students = Student.objects.all().order_by("-date_registered")
    return render(request, "portal/students_list.html", {"students": students})


def reports(request):
    all_reports = Report.objects.all().select_related("student").order_by("-date_sent")
    return render(request, "portal/reports.html", {"reports": all_reports})
''')

# ── portal/urls.py ───────────────────────────────────────────
write(os.path.join(PROJECT, "portal", "urls.py"), '''from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("register/", views.register, name="register"),
    path("students/", views.students_list, name="students_list"),
    path("reports/", views.reports, name="reports"),
]
''')

# ── portal/admin.py ──────────────────────────────────────────
write(os.path.join(PROJECT, "portal", "admin.py"), '''from django.contrib import admin
from .models import Student, Report
admin.site.register(Student)
admin.site.register(Report)
''')

# ── portal/tests.py ──────────────────────────────────────────
write(os.path.join(PROJECT, "portal", "tests.py"), "from django.test import TestCase\n")

# ── migrations ───────────────────────────────────────────────
touch(os.path.join(PROJECT, "portal", "migrations", "__init__.py"))

# ── Templates ────────────────────────────────────────────────
TMPL = os.path.join(PROJECT, "portal", "templates", "portal")

write(os.path.join(TMPL, "base.html"), '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PT4 Student Portal</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: Arial, sans-serif; background: #f0f2f5; color: #333; }
        nav { background: #2c3e50; padding: 14px 30px; display: flex; align-items: center; gap: 20px; }
        nav span { color: white; font-size: 18px; font-weight: bold; margin-right: auto; }
        nav a { color: #ccc; text-decoration: none; padding: 8px 16px; border-radius: 5px; font-size: 14px; }
        nav a:hover, nav a.active { background: #3498db; color: white; }
        .container { max-width: 1000px; margin: 30px auto; padding: 0 20px; }
        .card { background: white; border-radius: 8px; padding: 25px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); margin-bottom: 20px; }
        .card h2 { margin-bottom: 18px; color: #2c3e50; font-size: 20px; }
        .form-group { margin-bottom: 14px; }
        .form-group label { display: block; margin-bottom: 5px; font-weight: bold; font-size: 14px; }
        .form-group input { width: 100%; padding: 9px 12px; border: 1px solid #ccc; border-radius: 5px; font-size: 14px; }
        .form-group input:focus { outline: none; border-color: #3498db; }
        .form-row { display: flex; gap: 15px; }
        .form-row .form-group { flex: 1; }
        .btn { padding: 10px 22px; border: none; border-radius: 5px; font-size: 14px; cursor: pointer; font-weight: bold; }
        .btn-primary { background: #3498db; color: white; }
        .btn-primary:hover { background: #2980b9; }
        .messages { margin-bottom: 15px; }
        .msg { padding: 10px 15px; border-radius: 5px; margin-bottom: 8px; font-size: 14px; }
        .msg-success { background: #d4edda; color: #155724; border: 1px solid #c3e6cb; }
        .msg-error { background: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; }
        table { width: 100%; border-collapse: collapse; font-size: 14px; }
        th { background: #2c3e50; color: white; padding: 10px; text-align: left; }
        td { padding: 9px 10px; border-bottom: 1px solid #eee; }
        tr:hover td { background: #f8f9fa; }
    </style>
</head>
<body>
    <nav>
        <span> PT4 Student Portal</span>
        <a href="/register/" {% if request.path == \'/register/\' %}class="active"{% endif %}> Register</a>
        <a href="/students/" {% if request.path == \'/students/\' %}class="active"{% endif %}> Students</a>
        <a href="/reports/"  {% if request.path == \'/reports/\'  %}class="active"{% endif %}> Reports</a>
    </nav>
    <div class="container">
        {% if messages %}
        <div class="messages">
            {% for message in messages %}
            <div class="msg {% if message.tags == \'error\' %}msg-error{% else %}msg-success{% endif %}">{{ message }}</div>
            {% endfor %}
        </div>
        {% endif %}
        {% block content %}{% endblock %}
    </div>
</body>
</html>
''')

write(os.path.join(TMPL, "register.html"), '''{% extends "portal/base.html" %}
{% block content %}
<div class="card">
    <h2> Register New Student</h2>
    <form method="POST">
        {% csrf_token %}
        <div class="form-row">
            <div class="form-group">
                <label>Student ID Number *</label>
                <input type="text" name="student_id" placeholder="e.g. 2024-0001" required>
            </div>
            <div class="form-group">
                <label>Full Name *</label>
                <input type="text" name="name" placeholder="e.g. Juan Dela Cruz" required>
            </div>
        </div>
        <div class="form-group">
            <label>Password *</label>
            <input type="password" name="password" placeholder="Enter password" required>
        </div>
        <p style="font-weight:bold; margin-bottom:10px; color:#2c3e50;"> Grades (0-100)</p>
        <div class="form-row">
            <div class="form-group">
                <label>English</label>
                <input type="number" name="english_grade" placeholder="e.g. 90" min="0" max="100" step="0.01" required>
            </div>
            <div class="form-group">
                <label>Mathematics</label>
                <input type="number" name="math_grade" placeholder="e.g. 85" min="0" max="100" step="0.01" required>
            </div>
            <div class="form-group">
                <label>Science</label>
                <input type="number" name="science_grade" placeholder="e.g. 88" min="0" max="100" step="0.01" required>
            </div>
        </div>
        <button type="submit" class="btn btn-primary">Register Student</button>
    </form>
</div>
<div class="card">
    <h2> Registered Students (Confirmation)</h2>
    {% if students %}
    <table>
        <thead><tr><th>Student ID</th><th>Name</th><th>English</th><th>Math</th><th>Science</th><th>Date Registered</th></tr></thead>
        <tbody>
            {% for s in students %}
            <tr>
                <td>{{ s.student_id }}</td><td>{{ s.name }}</td>
                <td>{{ s.english_grade }}</td><td>{{ s.math_grade }}</td><td>{{ s.science_grade }}</td>
                <td>{{ s.date_registered|date:"Y-m-d H:i" }}</td>
            </tr>
            {% endfor %}
        </tbody>
    </table>
    {% else %}
    <p style="color:gray;">No students registered yet.</p>
    {% endif %}
</div>
{% endblock %}
''')

write(os.path.join(TMPL, "students_list.html"), '''{% extends "portal/base.html" %}
{% block content %}
<div class="card">
    <h2> All Registered Students</h2>
    {% if students %}
    <table>
        <thead><tr><th>#</th><th>Student ID</th><th>Name</th><th>English</th><th>Math</th><th>Science</th><th>Date Registered</th></tr></thead>
        <tbody>
            {% for s in students %}
            <tr>
                <td>{{ forloop.counter }}</td><td>{{ s.student_id }}</td><td>{{ s.name }}</td>
                <td>{{ s.english_grade }}</td><td>{{ s.math_grade }}</td><td>{{ s.science_grade }}</td>
                <td>{{ s.date_registered|date:"Y-m-d H:i" }}</td>
            </tr>
            {% endfor %}
        </tbody>
    </table>
    <p style="margin-top:10px; color:gray; font-size:13px;">Total: {{ students|length }} student(s)</p>
    {% else %}
    <p style="color:gray;">No students registered yet. <a href="/register/">Register one now</a></p>
    {% endif %}
</div>
{% endblock %}
''')

write(os.path.join(TMPL, "reports.html"), '''{% extends "portal/base.html" %}
{% block content %}
<div class="card">
    <h2> Student Reports and History</h2>
    {% if reports %}
    <table>
        <thead><tr><th>#</th><th>Student ID</th><th>Student Name</th><th>Message</th><th>Date Sent</th></tr></thead>
        <tbody>
            {% for r in reports %}
            <tr>
                <td>{{ forloop.counter }}</td><td>{{ r.student.student_id }}</td>
                <td>{{ r.student.name }}</td><td>{{ r.message }}</td>
                <td>{{ r.date_sent|date:"Y-m-d H:i" }}</td>
            </tr>
            {% endfor %}
        </tbody>
    </table>
    <p style="margin-top:10px; color:gray; font-size:13px;">Total: {{ reports|length }} report(s)</p>
    {% else %}
    <p style="color:gray;">No reports submitted yet. Students send reports from the desktop app.</p>
    {% endif %}
</div>
{% endblock %}
''')

# ── student_app.py already exists in pt4_portal, skip ────────
print("  Skipped: student_app.py already exists in pt4_portal")

print("\n All files created!\n")
print("Now running migrations...")

os.chdir(PROJECT)
result = subprocess.run([sys.executable, "manage.py", "migrate"], capture_output=True, text=True)
print(result.stdout)
if result.returncode != 0:
    print("Migration error:", result.stderr)
else:
    print(" Database ready!\n")

print("========================================")
print("  SETUP COMPLETE!")
print("========================================")
print()
print("To run System 1 (Django web):")
print("  cd pt4_portal")
print("  python manage.py runserver")
print("  Then open: http://127.0.0.1:8000/register/")
print()
print("To run System 2 (Desktop app):")
print("  cd pt4_portal")
print("  python student_app.py")
print()

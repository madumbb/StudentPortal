from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("register/", views.register, name="register"),
    path("students/", views.students_list, name="students_list"),
    path("reports/", views.reports, name="reports"),
]

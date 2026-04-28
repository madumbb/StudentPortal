from django.db import models


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
        return f"Report from {self.student.name} on {self.date_sent.strftime('%Y-%m-%d %H:%M')}"

from django.urls import path
from . import views

urlpatterns = [
    path("admin/enrollments/", views.manage_enroll, name="manage_enroll"),
    path('enroll_course/<int:course_id>/',views.enroll_course,name="enroll_course"),
]

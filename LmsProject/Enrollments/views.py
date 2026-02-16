from django.shortcuts import render,redirect
from .models import Enrollment
from Courses.models import *
from django.contrib import messages
from django.core.mail import send_mail
# Create your views here.
def manage_enroll(request):
    enrollments = Enrollment.objects.select_related('student', 'course').all()
    return render(request, "admin/manage_enroll.html", {"enrollments": enrollments})

def enroll_course(request, course_id):
    student = User.objects.get(id=request.session["user_id"])
    course = Course.objects.get(id=course_id)
    if not Enrollment.objects.filter(student=student,course=course).exists():
        Enrollment.objects.create(student=student,course=course)
        subject = f"Enrollment Confirmation:{course.title}"
        message = f"Hello {student.name},\n\nYou have successfully enrolled in the course '{course.title}'.\n\nHappy Learning!\n\n- LmsProject Team"
        recipient_list = [student.email]  
        send_mail(subject, message, None, recipient_list)
        messages.success(request, f"You have successfully enrolled in '{course.title}'! Check your email for confirmation.")
    else:
        messages.info(request, f"You are already enrolled in '{course.title}'.")
    return redirect('student_my_courses') 

from django.shortcuts import render,redirect,get_object_or_404
from .models import User
from Courses.models import Course,LessonProgress,QuizAttempt,Quiz,Certificate,Feedback
from Enrollments.models import Enrollment
from django.db.models import Count
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required
from django.db.models import Avg
from django.contrib import messages
from django.shortcuts import render
from Courses.models import QuizAttempt
from Users.models import User
import re
from django.contrib.auth.hashers import make_password
# Create your views here.

def redg_view(request):
    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        email = request.POST.get("email", "").strip()
        password = request.POST.get("password", "").strip()
        role = request.POST.get("role", "").strip()

        errors = {}

        # ---- Name validation ----
        if not name:
            errors["name"] = "Name is required"
        elif len(name.split()) < 2:
            errors["name"] = "Enter full name (at least 2 words)"

        # ---- Email validation ----
        if not email:
            errors["email"] = "Email is required"
        else:
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(email_pattern, email):
                errors["email"] = "Invalid email format"
            elif User.objects.filter(email=email).exists():
                errors["email"] = "Email already registered"

        # ---- Password validation ----
        if not password:
            errors["password"] = "Password is required"
        elif len(password) < 8:
            errors["password"] = "Password must be at least 8 characters"

        # ---- Role validation ----
        if role not in ["admin", "instructor", "student"]:
            errors["role"] = "Invalid role selected"

        # ---- If errors exist, re-render page with errors ----
        if errors:
            return render(request, "Users/register.html", {"errors": errors})

        # ---- Save user ----
        user = User.objects.create(
            name=name,
            email=email,
            password=make_password(password),  
            role=role
        )

        # ---- Store session ----
        request.session["user_id"] = user.id
        request.session["role"] = user.role

        # ---- Redirect based on role ----
        if role == "admin":
            return redirect("admin_dashboard")
        elif role == "instructor":
            return redirect("instr_dashboard")
        else:
            return redirect("student_dashboard")

    return render(request, "Users/register.html")

def admin_dashboard(request):
    user=User.objects.get(id=request.session["user_id"])
    users=User.objects.count()
    courses=Course.objects.count()
    enroll=Enrollment.objects.count()
    revenue=enroll*200  
    data = User.objects.values("role").annotate(count=Count("id"))
    labels = []
    counts = []
    for d in data:
        labels.append(d["role"])
        counts.append(d["count"])
    return render(request, "Users/admin_dashboard.html",{'user':user,'users':users,'courses':courses,'enroll':enroll,'revenue':revenue,'labels':labels,'counts':counts})

def instr_dashboard(request):
    user = User.objects.get(id=request.session["user_id"])
    courses = Course.objects.filter(instructor=user)
    count = courses.count()
    students = Enrollment.objects.filter(course__in=courses).count()
    course_data = []
    for course in courses:
        lessons_info = []
        for lesson in course.lesson_set.all():
            quiz_data = None
            if hasattr(lesson, 'quiz'):  
                quiz = lesson.quiz
                attempts = QuizAttempt.objects.filter(quiz=quiz)
                avg_score = attempts.aggregate(avg=Avg('score'))['avg'] or 0
                quiz_data = {
                    'id': quiz.id,
                    'attempted_students': attempts.count(),
                    'avg_score': round(avg_score, 2)
                }
            lessons_info.append({
                'lesson': lesson,
                'quiz': quiz_data
            })
        course_data.append({
            'course': course,
            'students': course.enrollment_set.count(),
            'lessons': lessons_info
        })
    return render(request, "Users/instr_dashboard.html", {
        'user': user,
        'courses': courses,
        'count': count,
        'students': students,
        'course_data': course_data
    })

def student_dashboard(request):
    if "user_id" not in request.session:
        return redirect("login") 
    student = User.objects.get(id=request.session["user_id"])
    courses = Enrollment.objects.filter(student=student)
    lesson_completed = LessonProgress.objects.filter(student=student, completed=True).count()
    quizzes_attempted = QuizAttempt.objects.filter(student=student).count()
    progress = 0
    if courses.exists():
        progress = sum(c.progress for c in courses) // courses.count()
    enrolled_course_ids = courses.values_list('course_id', flat=True)
    available_courses = Course.objects.exclude(id__in=enrolled_course_ids)
    quiz_attempts = {}
    for q in QuizAttempt.objects.filter(student=student):
        quiz_attempts[str(q.quiz.id)] = q.score  
    return render(request, "Users/student_dashboard.html", {
        "student": student,
        "courses": courses,
        "lesson_completed": lesson_completed,
        "quizzes_attempted": quizzes_attempted,
        "progress": progress,
        "available_courses": available_courses,
        "quiz_attempts": quiz_attempts,
    })

def login_view(request):
    if request.method=="POST":
        email=request.POST["email"]
        password=request.POST["password"]
        user=User.objects.filter(email=email,password=password).first()
        if user:
            request.session["user_id"]=user.id
            request.session["role"]=user.role
            if user.role=="admin":
                return redirect("admin_dashboard")
            elif user.role=="instructor":
                return redirect("instr_dashboard")
            else:
                return redirect("student_dashboard")
    return render(request,"Users/login.html")

def logout_view(request):
    request.session.flush()
    return redirect("login")

def manage_instr(request):
    instr=User.objects.filter(role='instructor')
    return render(request,'Users/manage_instr.html',{'instr': instr})

def manage_students(request):
    students=User.objects.filter(role='student')
    return render(request,'Users/manage_students.html',{'students': students})

def student_course(request, course_id):
    student = User.objects.get(id=request.session["user_id"])
    course = Course.objects.get(id=course_id)
    lessons = course.lesson_set.all()
    lesson_progress = {lp.lesson.id: lp.completed for lp in LessonProgress.objects.filter(student=student, lesson__in=lessons)}
    quiz_attempts = {qa.quiz.id: qa for qa in QuizAttempt.objects.filter(student=student, quiz__in=[l.quiz for l in lessons if l.quiz])}
    return render(request, "Users/student_course.html", {
        "student": student,
        "course": course,
        "lessons": lessons,
        "lesson_progress": lesson_progress,
        "quiz_attempts": quiz_attempts,
    })

def student_my_courses(request):
    s = User.objects.get(id=request.session["user_id"])
    enrolls = s.enrollment_set.all()
    data = []
    for e in enrolls:
        c = e.course
        lessons = []
        course_completed = True  
        for l in c.lesson_set.all():
            qa = None
            if hasattr(l, 'quiz'):
                qa = QuizAttempt.objects.filter(student=s, quiz=l.quiz).first()
                if not qa:  
                    course_completed = False
            lessons.append({'lesson': l, 'quiz': getattr(l, 'quiz', None), 'quiz_attempt': qa})
        data.append({'course': c, 'lessons': lessons, 'completed': course_completed})
    return render(request, "Students/my_courses.html", {'student': s, 'courses_data': data})

def course_feedback(request, course_id):
    student = User.objects.get(id=request.session["user_id"])
    course = Course.objects.get(id=course_id)
    if request.method == 'POST':
        feedback_text = request.POST.get('feedback')
        if feedback_text.strip():  
            Feedback.objects.create(student=student,course=course,feedback=feedback_text)
            messages.success(request, "Thank you for your feedback!")
            return redirect('student_my_courses')  
    existing_feedback = Feedback.objects.filter(student=student,course=course).first()
    return render(request, "Students/course_feedback.html", {
        'course': course,
        'existing_feedback': existing_feedback
    })

def student_progress(request):
    s = User.objects.get(id=request.session["user_id"])
    enrs = s.enrollment_set.all()
    data = []
    for e in enrs:
        course = e.course
        lessons = course.lesson_set.all()
        quizzes = Quiz.objects.filter(lesson__in=lessons)
        quiz_attempts =QuizAttempt.objects.filter(student=s, quiz__in=quizzes)
        quiz_done_lessons={qa.quiz.lesson.id for qa in quiz_attempts}
        lesson_done=LessonProgress.objects.filter(student=s, lesson__in=lessons, completed=True)
        lesson_done_ids={lp.lesson.id for lp in lesson_done}
        lessons_status={l.id: l.id in lesson_done_ids or l.id in quiz_done_lessons for l in lessons}
        done_lessons=sum(1 for completed in lessons_status.values() if completed)
        total_lessons=lessons.count()
        prog = (done_lessons*100) // total_lessons if total_lessons else 0
        data.append({
            'course': course,
            'lessons': lessons,
            'lessons_status': lessons_status,
            'done_les': done_lessons,
            'tot_les': total_lessons,
            'done_qus': len(quiz_attempts),
            'tot_qus': quizzes.count(),
            'prog': prog
        })
    return render(request, "Students/progress.html", {
        'student': s,
        'progress_data': data
    })

def student_certificates(request):
    s = User.objects.get(id=request.session["user_id"])
    certs = Certificate.objects.filter(student=s)
    return render(request, "Students/certificate.html", 
    {
        "student": s,
        "certificates": certs })

def manage_courses(request):
    courses = Course.objects.prefetch_related('lesson_set').all()
    return render(request, 'admin/manage_courses.html', {'courses':courses})

def edit_instructor(request, id):
    instructor = get_object_or_404(User, id=id, role="instructor")
    if request.method == "POST":
        instructor.name = request.POST.get("name")
        instructor.email = request.POST.get("email")
        instructor.role = request.POST.get("role")
        instructor.save()
        messages.success(request, "Instructor updated successfully!")
        return redirect("manage_instr")
    return render(request, "admin/edit_instr.html", {"instructor": instructor})

def delete_instructor(request, id):
    instr = get_object_or_404(User, id=id, role="instructor")
    instr.delete()
    messages.success(request, "Instructor deleted successfully!")
    return redirect("manage_instr")

def edit_student(request, id):
    student = get_object_or_404(User, id=id, role="student")
    if request.method == "POST":
        student.name = request.POST.get("name")
        student.email = request.POST.get("email")
        student.role = request.POST.get("role")
        student.save()
        messages.success(request, "Student updated successfully!")
        return redirect("manage_students")
    return render(request, "admin/edit_student.html", {"student": student})

def delete_student(request, id):
    student = get_object_or_404(User, id=id, role="student")
    student.delete()
    messages.success(request,"Student deleted successfully!")
    return redirect("manage_students")

def manage_instr_students(request):
    students=User.objects.filter(role='student')
    return render(request,'Users/manage_instr_students.html',{'students': students})
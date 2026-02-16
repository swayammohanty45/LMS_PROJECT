from django.shortcuts import render,redirect,get_object_or_404
from Users.models import User
from .models import Course,Lesson,Quiz,Question,QuizAttempt
from Enrollments.models import Enrollment
from django.db.models import Avg
from .forms import QuestionForm
from django.contrib import messages
import re

# Create your views here.
def add_course_view(request):
    user = User.objects.get(id=request.session["user_id"])
    if request.method == "POST":
        title=request.POST.get("title")
        description=request.POST.get("description")
        price=request.POST.get("price") 
        Course.objects.create(title=title,description=description,instructor=user,price=price)
        return redirect('instr_dashboard')
    return redirect('instr_dashboard')

def add_lesson_view(request,id):
    user=User.objects.get(id=request.session["user_id"])
    course=Course.objects.get(id=id,instructor=user)
    if request.method == "POST":
        title = request.POST.get("title")
        text = request.POST.get("text")
        video = request.POST.get("video")  
        Lesson.objects.create(course=course, title=title, text=text, video=video)
        return redirect('instr_dashboard') 
    return render(request,"Courses/add_lesson.html",{'course': course})

def course_list_view(request):
    courses = Course.objects.all()
    return render(request, "Courses/course_list.html", {"courses": courses})

def enroll_course_view(request, course_id):
    student = User.objects.get(id=request.session["user_id"])  
    course = get_object_or_404(Course, id=course_id)
    Enrollment.objects.create(student=student, course=course)
    return redirect("student_dashboard")

def add_quiz(request, id):
    lesson = get_object_or_404(Lesson, id=id)
    if request.method == "POST":
        title = request.POST.get("title")

        if not title:
            return render(request, "Courses/add_quiz.html", {
                "lesson": lesson,
                "error": "Quiz title required"
            })

        quiz = Quiz.objects.create(lesson=lesson, title=title)

        for i in range(1, 3): 
            q_text = request.POST.get(f"question_{i}", "").strip()
            optA = request.POST.get(f"optionA_{i}", "").strip()
            optB = request.POST.get(f"optionB_{i}", "").strip()
            optC = request.POST.get(f"optionC_{i}", "").strip()
            optD = request.POST.get(f"optionD_{i}", "").strip()
            ans = request.POST.get(f"answer_{i}", "").strip()

            if q_text:
                if len(q_text.split()) < 3:  
                    return render(request, "Courses/add_quiz.html", {
                        "lesson": lesson,
                        "error": f"Question {i} must be more than one word"
                    })

                if q_text.isdigit():  
                    return render(request, "Courses/add_quiz.html", {
                        "lesson": lesson,
                        "error": f"Question {i} cannot be just a number"
                    })
            if optA and optB and optC and optD and ans:
                Question.objects.create(
                    quiz=quiz,
                    text=q_text,
                    optionA=optA,
                    optionB=optB,
                    optionC=optC,
                    optionD=optD,
                    answer=ans
                )
            else:
                return render(request, "Courses/add_quiz.html", {
                    "lesson": lesson,
                    "error": f"All options and answer required for Question {i}"
                })

        return redirect("view_quiz", id=quiz.id)

    return render(request, "Courses/add_quiz.html", {"lesson": lesson})

def view_quiz(request,id):
    quiz=get_object_or_404(Quiz, id=id)
    questions=quiz.question_set.all()
    return render(request, "Courses/view_quiz.html", {
        "quiz": quiz,
        "questions": questions,
    })

def instr_quiz_view(request):
    user = User.objects.get(id=request.session["user_id"])
    courses = Course.objects.filter(instructor=user)
    quiz_data = []
    for course in courses:
        for lesson in course.lesson_set.all():
            quiz = getattr(lesson, 'quiz', None)  
            if quiz: 
                attempts = QuizAttempt.objects.filter(quiz=quiz)
                attempted_students = attempts.count()
                avg_score = attempts.aggregate(avg=Avg('score'))['avg'] or 0

                quiz_data.append({
                    "quiz": quiz,
                    "lesson": lesson,
                    "course": course,
                    "attempted_students": attempted_students,
                    "avg_score": round(avg_score, 2),
                })

    return render(request, "Courses/instr_quizzes_list.html", {
        "quiz_data": quiz_data,
    })

MAX_ATTEMPTS = 2
PASS_PERCENT = 70
def quiz(request, id):
    student = User.objects.get(id=request.session["user_id"])
    quiz = get_object_or_404(Quiz, id=id)
    questions = quiz.question_set.all()
    attempts_obj = QuizAttempt.objects.filter(student=student, quiz=quiz).first()
    attempts_done = attempts_obj.attempts if attempts_obj else 0
    if attempts_done >= MAX_ATTEMPTS:
        return render(request, "Courses/result.html", {
            "quiz": quiz,
            "score": None,
            "total": len(questions),
            "message": f"You have used all {MAX_ATTEMPTS} attempts."
        })
    if request.method == "POST":
        score=0
        for q in questions:
            if request.POST.get(f"q{q.id}")==q.answer:
                score+=1
        q_attempt,created = QuizAttempt.objects.get_or_create(student=student, quiz=quiz)
        q_attempt.score = score
        q_attempt.attempts = (q_attempt.attempts or 0) + 1
        q_attempt.save()
        enrollment=Enrollment.objects.get(student=student, course=quiz.lesson.course)
        total_quizzes=Quiz.objects.filter(lesson__course=quiz.lesson.course).count()
        completed_quizzes=QuizAttempt.objects.filter(student=student, quiz__lesson__course=quiz.lesson.course).count()
        enrollment.progress=(completed_quizzes * 100) // total_quizzes
        enrollment.save()
        passed=(score / len(questions))*100>=PASS_PERCENT
        return render(request,"Courses/result.html",{
            "quiz": quiz,
            "score": score,
            "total": len(questions),
            "passed": passed,
            "attempts_left": MAX_ATTEMPTS-q_attempt.attempts
        })
    return render(request, "Courses/quiz.html", {"quiz": quiz, "questions": questions})

def manage_lessons_view(request):
    user = User.objects.get(id=request.session["user_id"])   
    courses = Course.objects.filter(instructor=user)
    course_data = []
    for course in courses:
        lessons = Lesson.objects.filter(course=course)
        course_data.append({
            "course":course,
            "students":Enrollment.objects.filter(course=course).count(),
            "lessons":[{"lesson": l} for l in lessons],
        })
    return render(request, "Courses/manage_lessons.html", {"course_data": course_data})

def add_question(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    if request.method == "POST":
        form = QuestionForm(request.POST)
        if form.is_valid():
            question = form.save(commit=False)
            question.quiz = quiz
            question.save()
            messages.success(request, "Question added successfully!")
            return redirect("view_quiz",id=question.quiz.id)
    else:
        form = QuestionForm()
    return render(request, "courses/edit_question.html", {"form": form, "quiz": quiz})

def edit_question(request, question_id):
    question = get_object_or_404(Question,id=question_id)
    if request.method == "POST":
        form = QuestionForm(request.POST,instance=question)
        if form.is_valid():
            form.save()
            messages.success(request,"Question updated successfully!")
            return redirect("view_quiz",id=question.quiz.id)
    else:
        form = QuestionForm(instance=question)
    return render(request, "courses/edit_question.html", {"form": form, "quiz": question.quiz})

def delete_question(request, question_id):
    question = get_object_or_404(Question,id=question_id)
    quiz = question.quiz
    if request.method == 'POST':
        question.delete()
        messages.success(request, f"'{question.text}'Question deleted successfully!")
    return redirect("view_quiz")
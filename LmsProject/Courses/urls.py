from django.urls import path
from . import views

urlpatterns = [
    path('add-course/', views.add_course_view, name='add_course'),
    path('add-lesson/<int:id>/', views.add_lesson_view, name='add_lesson'),
    path("courses/", views.course_list_view, name="course_list"),
    path("courses/enroll/<int:course_id>/", views.enroll_course_view, name="enroll_course"),
    path("addquiz/<int:id>/", views.add_quiz, name="add_quiz"),
    path("quiz/<int:id>/", views.quiz, name="quiz"),
    path('instr-quizzes/', views.instr_quiz_view, name='instr_quizzes'),
    path('manage-lessons/', views.manage_lessons_view, name='manage_lessons'),
    path("view_quiz/<int:id>/", views.view_quiz, name="view_quiz"),
    path("quiz/<int:quiz_id>/add-question/", views.add_question, name="add_question"),
    path("question/<int:question_id>/edit/", views.edit_question, name="edit_question"),
    path("question/<int:question_id>/delete/", views.delete_question, name="delete_question"),

]

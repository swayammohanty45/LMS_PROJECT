from django.urls import path
from .import views

urlpatterns = [
    path("register/", views.redg_view, name="redg"),
    path("admin-dashboard/", views.admin_dashboard, name="admin_dashboard"),
    path("instr-dashboard/", views.instr_dashboard, name="instr_dashboard"),
    path("edit_instructor/<int:id>/", views.edit_instructor, name="edit_instr"),
    path("delete_instructor/<int:id>/", views.delete_instructor, name="delete_instr"),
    path("student-dashboard/", views.student_dashboard, name="student_dashboard"),
    path("edit-student/<int:id>/", views.edit_student, name="edit_student"),
    path("delete-student/<int:id>/", views.delete_student, name="delete_student"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("manage_instr",views.manage_instr,name="manage_instr"),
    path("manage_students",views.manage_students,name="manage_students"),
    path("manage_instr_students",views.manage_instr_students,name="manage_instr_students"),
    path('my-courses/', views.student_my_courses, name='student_my_courses'),
    path('progress/', views.student_progress, name='student_progress'),
    path('certificates/', views.student_certificates, name='student_certificates'),
    path('admin/manage-courses/', views.manage_courses, name='manage_courses'),
    path('course/<int:course_id>/feedback/', views.course_feedback, name='course_feedback')

]

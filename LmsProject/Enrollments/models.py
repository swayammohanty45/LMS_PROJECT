from django.db import models
from Users.models import User
from Courses.models import Course
# Create your models here.
class Enrollment(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    progress = models.IntegerField(default=0)  
    completed = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.student.name} - {self.course.title}"
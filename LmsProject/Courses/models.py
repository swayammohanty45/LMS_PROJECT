from django.db import models
from Users.models import User

# Create your models here.
class Course(models.Model):
    title=models.CharField(max_length=320)
    description=models.TextField()
    instructor=models.ForeignKey(User, on_delete=models.CASCADE)  
    price=models.IntegerField()   

    def __str__(s):
        return s.title

class Lesson(models.Model):
    course=models.ForeignKey(Course, on_delete=models.CASCADE)
    title=models.CharField(max_length=500)
    text=models.TextField()   
    video=models.CharField(max_length=200, null=True, blank=True)  

    def __str__(s):
        return s.title
    
class Quiz(models.Model):
    lesson = models.OneToOneField(Lesson, on_delete=models.CASCADE, related_name="quiz")
    title=models.CharField(max_length=200)

    def __str__(s):
        return s.title

class Question(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    text = models.CharField(max_length=255)
    optionA = models.CharField(max_length=100,default='')
    optionB = models.CharField(max_length=100,default='')
    optionC = models.CharField(max_length=100,default='')
    optionD = models.CharField(max_length=100,default='')
    answer = models.CharField(max_length=1) 
    
    def __str__(self):
        return self.text

class LessonProgress(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE)
    completed = models.BooleanField(default=False)
  
    def __str__(s):
        return s.student.name

class QuizAttempt(models.Model):
    student = models.ForeignKey(User,on_delete=models.CASCADE)
    quiz = models.ForeignKey(Quiz,on_delete=models.CASCADE)
    attempts = models.IntegerField(default=0)
    score = models.IntegerField(default=0)

    def __str__(s):
        return s.student.name
    
class Certificate(models.Model):
    student = models.ForeignKey(User,on_delete=models.CASCADE)
    course = models.ForeignKey(Course,on_delete=models.CASCADE)
    grade = models.IntegerField(default=0)
    awarded_on = models.DateField(auto_now_add=True)
    file = models.FileField(upload_to='certificates/', blank=True, null=True)

class Feedback(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    feedback = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student.name} - {self.course.title}"
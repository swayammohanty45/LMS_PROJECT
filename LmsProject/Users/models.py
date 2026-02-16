from django.db import models

# Create your models here.
class User(models.Model):
    role = [
        ('student', 'Student'),
        ('instructor', 'Instructor'),
        ('admin', 'Admin'),
    ]
    name=models.CharField(max_length=34)
    email=models.EmailField(unique=True)
    password = models.CharField(max_length=128)    
    role=models.CharField(max_length=13,choices=role)
    
    def __str__(self):
        return self.name
    
    
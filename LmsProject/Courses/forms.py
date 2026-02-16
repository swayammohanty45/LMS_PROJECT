from django import forms
from .models import Question

class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['text', 'optionA', 'optionB', 'optionC', 'optionD', 'answer']
        widgets = {
            'text': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'optionA': forms.TextInput(attrs={'class': 'form-control'}),
            'optionB': forms.TextInput(attrs={'class': 'form-control'}),
            'optionC': forms.TextInput(attrs={'class': 'form-control'}),
            'optionD': forms.TextInput(attrs={'class': 'form-control'}),
            'answer': forms.Select(attrs={'class': 'form-select'}, choices=[
                ('A', 'Option A'),
                ('B', 'Option B'),
                ('C', 'Option C'),
                ('D', 'Option D'),
            ])
        }


from django import forms
from .models import User

class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = [
            'username',
            'email',
            'profile_picture',
            'bio'
        ]
        widgets = {
            'bio': forms.Textarea(attrs={
                'rows': 6,
                'placeholder': 'Write your bio ...',
            }),
        }

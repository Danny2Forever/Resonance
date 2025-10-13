from django import forms
from .models import User
from django.core.exceptions import ValidationError
import re

class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'favorite_song', 'profile_picture', 'bio']
        widgets = {
            'bio': forms.Textarea(attrs={
                'rows': 5,
                'placeholder': 'Tell us about yourself...',
            }),
            'username': forms.TextInput(attrs={
            }),
            'favorite_song': forms.URLInput(attrs={
                'placeholder': 'https://open.spotify.com/track/...'
            }),
            'profile_picture': forms.FileInput(attrs={'class': 'hidden'}),
        }
        labels = {
            'username': '',
            'favorite_song': '',
            'bio': '',
        }

    def clean_favorite_song(self):
        """Valid spotify url."""
        url = self.cleaned_data.get('favorite_song')

        if not url:
            return url

        pattern = r"^https:\/\/open\.spotify\.com\/track\/[A-Za-z0-9]+"
        if not re.match(pattern, url):
            raise forms.ValidationError("Please enter a valid Spotify track URL (e.g. https://open.spotify.com/track/...)")

        return url

from django import forms
from .models import MediaItem

class MediaItemForm(forms.ModelForm):
    class Meta:
        model = MediaItem
        fields = ['title', 'description', 'media_type', 'release_date', 'poster']
        widgets = {
            'release_date': forms.DateInput(attrs={'type': 'date'}),
        }

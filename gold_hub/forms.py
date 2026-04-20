from django import forms
from .models import Poll, PollOption, PlayerStat, ClubStat


class PollForm(forms.ModelForm):
    class Meta:
        model = Poll
        fields = ('title', 'description', 'month_label', 'is_active')
        widgets = {
            'title':       forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'month_label': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. April 2025'}),
            'is_active':   forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class PollOptionForm(forms.ModelForm):
    class Meta:
        model = PollOption
        fields = ('player_name', 'description', 'image', 'order')
        widgets = {
            'player_name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 3 goals vs Arsenal'}),
            'image':       forms.FileInput(attrs={'class': 'form-control'}),
            'order':       forms.NumberInput(attrs={'class': 'form-control'}),
        }


class PlayerStatForm(forms.ModelForm):
    class Meta:
        model = PlayerStat
        fields = ('name', 'position', 'image', 'season', 'appearances',
                  'goals', 'assists', 'clean_sheets', 'rating', 'order')
        widgets = {
            'name':         forms.TextInput(attrs={'class': 'form-control'}),
            'position':     forms.Select(attrs={'class': 'form-select'}),
            'image':        forms.FileInput(attrs={'class': 'form-control'}),
            'season':       forms.TextInput(attrs={'class': 'form-control', 'placeholder': '2024/25'}),
            'appearances':  forms.NumberInput(attrs={'class': 'form-control'}),
            'goals':        forms.NumberInput(attrs={'class': 'form-control'}),
            'assists':      forms.NumberInput(attrs={'class': 'form-control'}),
            'clean_sheets': forms.NumberInput(attrs={'class': 'form-control'}),
            'rating':       forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1'}),
            'order':        forms.NumberInput(attrs={'class': 'form-control'}),
        }


class ClubStatForm(forms.ModelForm):
    class Meta:
        model = ClubStat
        fields = ('season', 'competition', 'played', 'won', 'drawn', 'lost',
                  'goals_for', 'goals_against', 'position', 'points', 'is_current')
        widgets = {
            'season':        forms.TextInput(attrs={'class': 'form-control', 'placeholder': '2024/25'}),
            'competition':   forms.TextInput(attrs={'class': 'form-control'}),
            'played':        forms.NumberInput(attrs={'class': 'form-control'}),
            'won':           forms.NumberInput(attrs={'class': 'form-control'}),
            'drawn':         forms.NumberInput(attrs={'class': 'form-control'}),
            'lost':          forms.NumberInput(attrs={'class': 'form-control'}),
            'goals_for':     forms.NumberInput(attrs={'class': 'form-control'}),
            'goals_against': forms.NumberInput(attrs={'class': 'form-control'}),
            'position':      forms.NumberInput(attrs={'class': 'form-control'}),
            'points':        forms.NumberInput(attrs={'class': 'form-control'}),
            'is_current':    forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

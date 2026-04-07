from django import forms
from .models import TransferRumour


class TransferRumourForm(forms.ModelForm):
    class Meta:
        model = TransferRumour
        fields = ['player_name', 'current_club', 'position', 'age', 'fee', 'source', 'likelihood']
        widgets = {
            'player_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Victor Osimhen'}),
            'current_club': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Napoli'}),
            'position': forms.Select(attrs={'class': 'form-select'}),
            'age': forms.NumberInput(attrs={'class': 'form-control', 'min': 15, 'max': 45}),
            'fee': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. £75m or Free'}),
            'source': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://... (optional)'}),
            'likelihood': forms.NumberInput(attrs={
                'class': 'form-range', 'type': 'range', 'min': 1, 'max': 10, 'id': 'likelihoodSlider'
            }),
        }

    def clean_likelihood(self):
        val = self.cleaned_data.get('likelihood')
        if not (1 <= val <= 10):
            raise forms.ValidationError("Likelihood must be between 1 and 10.")
        return val

    def clean_age(self):
        age = self.cleaned_data.get('age')
        if not (15 <= age <= 45):
            raise forms.ValidationError("Please enter a realistic age (15–45).")
        return age

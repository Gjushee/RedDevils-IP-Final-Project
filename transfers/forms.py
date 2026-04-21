import re
from django import forms
from .models import TransferRumour


class TransferRumourForm(forms.ModelForm):
    class Meta:
        model = TransferRumour
        fields = ['player_name', 'current_club', 'position', 'age', 'fee', 'source', 'likelihood']
        widgets = {
            'player_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g. Victor Osimhen',
                'minlength': '2',
                'maxlength': '100',
            }),
            'current_club': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g. Napoli',
                'minlength': '2',
                'maxlength': '100',
            }),
            'position': forms.Select(attrs={'class': 'form-select'}),
            'age': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 15,
                'max': 45,
                'placeholder': '24',
            }),
            'fee': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g. £75m or Free',
                'maxlength': '50',
            }),
            'source': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://... (optional)',
            }),
            'likelihood': forms.NumberInput(attrs={
                'class': 'form-range',
                'type': 'range',
                'min': 1,
                'max': 10,
                'id': 'likelihoodSlider',
            }),
        }

    def clean_player_name(self):
        name = self.cleaned_data.get('player_name', '').strip()
        if len(name) < 2:
            raise forms.ValidationError("Player name must be at least 2 characters long.")
        if not re.match(r"^[A-Za-zÀ-ÿ\s\-'\.]+$", name):
            raise forms.ValidationError(
                "Player name can only contain letters, spaces, hyphens, and apostrophes."
            )
        if re.search(r'(.)\1{4,}', name):
            raise forms.ValidationError("Player name does not look valid — repeated characters detected.")
        return name

    def clean_current_club(self):
        club = self.cleaned_data.get('current_club', '').strip()
        if len(club) < 2:
            raise forms.ValidationError("Club name must be at least 2 characters long.")
        if not re.match(r"^[A-Za-zÀ-ÿ0-9\s\-'\.&]+$", club):
            raise forms.ValidationError("Club name contains invalid characters.")
        if re.search(r'(.)\1{4,}', club):
            raise forms.ValidationError("Club name does not look valid — repeated characters detected.")
        return club

    def clean_age(self):
        age = self.cleaned_data.get('age')
        if age is None:
            raise forms.ValidationError("Age is required.")
        if not (15 <= age <= 45):
            raise forms.ValidationError("Please enter a realistic player age between 15 and 45.")
        return age

    def clean_fee(self):
        fee = self.cleaned_data.get('fee', '').strip()
        if not fee:
            raise forms.ValidationError("Transfer fee is required.")
        if len(fee) > 50:
            raise forms.ValidationError("Fee description is too long (max 50 characters).")
        if not re.match(
            r'^(free|loan|tbd|undisclosed|[~£€$]?[\d\s\.,]+\s*[mMbBkK]?)$',
            fee,
            re.IGNORECASE,
        ):
            raise forms.ValidationError(
                "Enter a valid fee — e.g. £75m, €50m, Free, Loan, or Undisclosed."
            )
        return fee

    def clean_source(self):
        url = self.cleaned_data.get('source', '').strip()
        if url and not re.match(r'^https?://', url, re.IGNORECASE):
            raise forms.ValidationError("Please enter a valid URL starting with http:// or https://")
        return url

    def clean_likelihood(self):
        val = self.cleaned_data.get('likelihood')
        if val is None or not (1 <= val <= 10):
            raise forms.ValidationError("Likelihood must be between 1 and 10.")
        return val

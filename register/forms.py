import re
from django import forms
from django.contrib.auth.models import User
from .models import Profile
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm





class RegistrationForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'you@example.com',
        }),
        help_text='Required. A verification link will be sent to this address.'
    )
    full_name = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'John Smith (optional)',
        }),
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'full_name', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Choose a username',
        })
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Create a password',
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Confirm your password',
        })
        self.fields['username'].help_text = 'Letters, digits, and @/./+/-/_ only.'
        self.fields['password1'].help_text = (
            'Min 8 characters. Must contain at least one letter and one number.'
        )
        self.fields['password2'].help_text = 'Enter the same password again to confirm.'

    def clean_email(self):
        email = self.cleaned_data.get('email', '').lower()
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('An account with this email already exists.')
        return email

    def clean_password1(self):
        password = self.cleaned_data.get('password1', '')
        if len(password) < 8:
            raise forms.ValidationError('Password must be at least 8 characters long.')
        if not re.search(r'[A-Za-z]', password):
            raise forms.ValidationError('Password must contain at least one letter.')
        if not re.search(r'\d', password):
            raise forms.ValidationError('Password must contain at least one number.')
        return password


class LoginForm(forms.Form):
    username = forms.CharField(
        label='Username or Email',
        max_length=254,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Username or email address',
            'autofocus': True,
        }),
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Your password',
        }),
    )


class EditProfileForm(forms.ModelForm):
    first_name = forms.CharField(
        max_length=100, required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First name'}),
    )
    last_name = forms.CharField(
        max_length=100, required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last name'}),
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control'}),
    )

    class Meta:
        model = Profile
        fields = ('full_name', 'bio', 'profile_image', 'favourite_player', 'date_of_birth', 'phone_number')
        widgets = {
            'full_name': forms.TextInput(attrs={
                'class': 'form-control', 'placeholder': 'Your full name',
            }),
            'bio': forms.Textarea(attrs={
                'class': 'form-control', 'rows': 3, 'placeholder': 'Tell us about yourself...',
            }),
            'profile_image': forms.FileInput(attrs={'class': 'form-control'}),
            'favourite_player': forms.TextInput(attrs={
                'class': 'form-control', 'placeholder': 'e.g. Bruno Fernandes',
            }),
            'date_of_birth': forms.DateInput(attrs={
                'class': 'form-control', 'type': 'date',
            }),
            'phone_number': forms.TextInput(attrs={
                'class': 'form-control', 'placeholder': '+44 7700 000000',
            }),
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        if user:
            self.fields['first_name'].initial = user.first_name
            self.fields['last_name'].initial  = user.last_name
            self.fields['email'].initial      = user.email

    def clean_email(self):
        email = self.cleaned_data.get('email', '').lower()
        return email


# new class to add before MembershipPaymentForm:
class StyledPasswordChangeForm(PasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})
        self.fields['old_password'].widget.attrs['placeholder']  = 'Enter your current password'
        self.fields['new_password1'].widget.attrs['placeholder'] = 'Create a new password'
        self.fields['new_password2'].widget.attrs['placeholder'] = 'Confirm your new password'



class MembershipPaymentForm(forms.Form):
    card_name   = forms.CharField(max_length=100, widget=forms.TextInput(attrs={
        'class': 'form-control', 'placeholder': 'Name on card', 'id': 'memCardName',
    }))
    card_number = forms.CharField(max_length=19, widget=forms.TextInput(attrs={
        'class': 'form-control', 'placeholder': '1234 5678 9012 3456',
        'id': 'memCardNumber', 'maxlength': '19', 'inputmode': 'numeric',
    }))
    expiry      = forms.CharField(max_length=5, widget=forms.TextInput(attrs={
        'class': 'form-control', 'placeholder': 'MM/YY',
        'id': 'memExpiry', 'maxlength': '5', 'inputmode': 'numeric',
    }))
    cvv         = forms.CharField(max_length=4, widget=forms.TextInput(attrs={
        'class': 'form-control', 'placeholder': '•••',
        'id': 'memCvv', 'maxlength': '4', 'inputmode': 'numeric',
    }))

    def clean_card_number(self):
        number = self.cleaned_data.get('card_number', '').replace(' ', '')
        if not number.isdigit() or len(number) not in (15, 16):
            raise forms.ValidationError('Enter a valid 15 or 16 digit card number.')
        return number

    def clean_expiry(self):
        expiry = self.cleaned_data.get('expiry', '')
        if len(expiry) != 5 or expiry[2] != '/' or not expiry[:2].isdigit() or not expiry[3:].isdigit():
            raise forms.ValidationError('Enter expiry as MM/YY.')
        month = int(expiry[:2])
        if not (1 <= month <= 12):
            raise forms.ValidationError('Enter a valid month (01–12).')
        return expiry

    def clean_cvv(self):
        cvv = self.cleaned_data.get('cvv', '')
        if not cvv.isdigit() or len(cvv) not in (3, 4):
            raise forms.ValidationError('Enter a valid 3 or 4 digit CVV.')
        return cvv

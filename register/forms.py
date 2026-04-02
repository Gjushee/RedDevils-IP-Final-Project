import re
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
 
 
class RegistrationForm(UserCreationForm):
    """
    Extended registration form.
    Adds email (required + unique) and full name.
    Enforces password rules beyond Django defaults.
    """
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
        # Style all fields with Bootstrap classes
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
        # Clean up the default help texts
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
    """
    Simple login form — accepts username or email.
    """
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
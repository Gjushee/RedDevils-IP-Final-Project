from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.conf import settings
 
from .forms import RegistrationForm, LoginForm
from .models import Profile
 
 
# ──────────────────────────────────────────────
# REGISTER
# ──────────────────────────────────────────────
def register_view(request):
    if request.user.is_authenticated:
        return redirect('core:home')
 
    form = RegistrationForm()
 
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            # Save user but don't log in yet — email must be verified first
            user = form.save(commit=False)
            user.email = form.cleaned_data['email']
            user.is_active = True   # Account is active; just not email-verified
            user.save()
 
            # Create the Profile
            profile = Profile.objects.create(user=user)
            full_name = form.cleaned_data.get('full_name', '')
            if full_name:
                profile.full_name = full_name
                profile.save()
 
            # Send verification email
            _send_verification_email(request, user, profile)
 
            messages.success(
                request,
                f'Account created! Please check {user.email} to verify your account before logging in.'
            )
            return redirect('register:login')
 
    return render(request, 'register/register.html', {'form': form})
 
 
# ──────────────────────────────────────────────
# EMAIL VERIFICATION
# ──────────────────────────────────────────────
def verify_email(request, token):
    profile = get_object_or_404(Profile, verification_token=token)
 
    if profile.email_verified:
        messages.info(request, 'Your email is already verified. Please log in.')
    else:
        profile.email_verified = True
        profile.save()
        messages.success(request, 'Email verified successfully! You can now log in.')
 
    return redirect('register:login')
 
 
def _send_verification_email(request, user, profile):
    verify_url = request.build_absolute_uri(
        f'/register/verify/{profile.verification_token}/'
        f'/verify/{profile.verification_token}/'
    )
    subject = 'Red Devils Hub — Verify your email'
    message =  (
        f'Hi {user.username},\n\n'
        f'Thanks for registering at Red Devils Hub!\n\n'
        f'Please click the link below to verify your email address:\n\n'
        f'{verify_url}\n\n'
        f'If you did not create this account you can ignore this email.\n\n'
        f'COYР — Red Devils Hub'
    )
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
        fail_silently=False,
    )
 
 
# ──────────────────────────────────────────────
# LOGIN
# ──────────────────────────────────────────────
def login_view(request):
    if request.user.is_authenticated:
        return _redirect_by_role(request.user)
 
    form = LoginForm()
 
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            raw_input = form.cleaned_data['username']
            password  = form.cleaned_data['password']
 
            # Allow login with email OR username
            username = _resolve_username(raw_input)
            user = authenticate(request, username=username, password=password)
 
            if user is not None:
                # Check email is verified
                try:
                    profile = user.profile
                except Profile.DoesNotExist:
                    profile = Profile.objects.create(user=user)
 
                if not profile.email_verified:
                    messages.warning(
                        request,
                        'Please verify your email before logging in. '
                        'Check your inbox for the verification link.'
                    )
                    return render(request, 'register/login.html', {'form': form})
 
                login(request, user)
                messages.success(request, f'Welcome back, {user.username}!')
                return _redirect_by_role(user)
            else:
                messages.error(request, 'Invalid username/email or password.')
 
    return render(request, 'register/login.html', {'form': form})
 
 
def _resolve_username(raw_input):
    """If the user typed an email, find the matching username."""
    if '@' in raw_input:
        try:
            return User.objects.get(email__iexact=raw_input).username
        except User.DoesNotExist:
            pass
    return raw_input
 
 
def _redirect_by_role(user):
    """Send users to the right page based on their role."""
    try:
        role = user.profile.role
    except Profile.DoesNotExist:
        role = 'free'
 
    if role == 'admin':
        return redirect('register:admin_dashboard')
    return redirect('core:home')
 
 
# ──────────────────────────────────────────────
# LOGOUT
# ──────────────────────────────────────────────
def logout_view(request):
    logout(request)
    messages.success(request, 'You have been logged out.')
    return redirect('core:home')
 
 
# ──────────────────────────────────────────────
# ADMIN DASHBOARD (custom — not Django's /admin/)
# ──────────────────────────────────────────────
def admin_dashboard(request):
    from .decorators import admin_required
    # Manually apply check here so we can return a proper response
    if not request.user.is_authenticated:
        messages.error(request, 'Please log in.')
        return redirect('register:login')
    try:
        if not request.user.profile.is_admin():
            messages.error(request, 'Access denied. Admin only.')
            return redirect('core:home')
    except Profile.DoesNotExist:
        messages.error(request, 'Access denied.')
        return redirect('core:home')
 
    total_users = User.objects.count()
    recent_users = User.objects.order_by('-date_joined')[:10]
 
    context = {
        'total_users': total_users,
        'recent_users': recent_users,
    }
    return render(request, 'register/admin_dashboard.html', context)
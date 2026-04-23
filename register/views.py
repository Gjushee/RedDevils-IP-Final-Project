from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.conf import settings

from django.contrib.auth.decorators import login_required

from .forms import RegistrationForm, LoginForm, EditProfileForm, MembershipPaymentForm, StyledPasswordChangeForm
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
            user = form.save(commit=False)
            user.email = form.cleaned_data['email']
            user.is_active = True
            user.save()

            profile = Profile.objects.create(user=user)
            full_name = form.cleaned_data.get('full_name', '')
            if full_name:
                profile.full_name = full_name
                profile.save()

            verify_url = request.build_absolute_uri(
                f'/verify/{profile.verification_token}/'
            )
            request.session['pending_verify_url']   = verify_url
            request.session['pending_verify_email'] = user.email

            try:
                _send_verification_email(request, user, profile)
            except Exception:
                pass

            return redirect('register:register_success')

    return render(request, 'register/register.html', {'form': form})


def register_success(request):
    verify_url = request.session.pop('pending_verify_url', None)
    email      = request.session.pop('pending_verify_email', None)
    if not verify_url:
        return redirect('register:register')
    return render(request, 'register/register_success.html', {
        'verify_url': verify_url,
        'email': email,
    })


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
        f'/verify/{profile.verification_token}/'
    )
    subject = 'Red Devils Hub — Verify your email'
    message = (
        f'Hi {user.username},\n\n'
        f'Thanks for registering at Red Devils Hub!\n\n'
        f'Please click the link below to verify your email address:\n\n'
        f'{verify_url}\n\n'
        f'If you did not create this account you can ignore this email.\n\n'
        f'COYR — Red Devils Hub'
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

            username = _resolve_username(raw_input)
            user = authenticate(request, username=username, password=password)

            if user is not None:
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
    if '@' in raw_input:
        try:
            return User.objects.get(email__iexact=raw_input).username
        except User.DoesNotExist:
            pass
    return raw_input


def _redirect_by_role(user):
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
# ADMIN DASHBOARD
# ──────────────────────────────────────────────
def admin_dashboard(request):
    from .decorators import admin_required
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

    all_users = User.objects.select_related('profile').order_by('-date_joined')
    total_users = all_users.count()

    role_counts = {
        'free':  Profile.objects.filter(role='free').count(),
        'red':   Profile.objects.filter(role='red').count(),
        'gold':  Profile.objects.filter(role='gold').count(),
        'admin': Profile.objects.filter(role='admin').count(),
    }

    try:
        from transfers.models import TransferRumour
        pending_rumours = TransferRumour.objects.filter(status='pending').count()
        recent_rumours  = TransferRumour.objects.filter(status='pending').order_by('-submitted_at')[:5]
    except Exception:
        pending_rumours = 0
        recent_rumours  = []

    try:
        from catalogue.models import Product
        total_products = Product.objects.count()
    except Exception:
        total_products = 0

    try:
        from core.models import ContactMessage
        contact_messages = ContactMessage.objects.all()
        unread_messages  = contact_messages.filter(is_read=False).count()
    except Exception:
        contact_messages = []
        unread_messages  = 0

    context = {
        'all_users':        all_users,
        'total_users':      total_users,
        'role_counts':      role_counts,
        'pending_rumours':  pending_rumours,
        'recent_rumours':   recent_rumours,
        'contact_messages': contact_messages,
        'unread_messages':  unread_messages,
        'total_products':   total_products,
    }
    return render(request, 'register/admin_dashboard.html', context)


# ──────────────────────────────────────────────
# ADMIN — CHANGE USER ROLE
# ──────────────────────────────────────────────
def change_user_role(request, user_id):
    if not request.user.is_authenticated:
        return redirect('register:login')
    try:
        if not request.user.profile.is_admin():
            messages.error(request, 'Access denied.')
            return redirect('core:home')
    except Profile.DoesNotExist:
        return redirect('core:home')

    if request.method == 'POST':
        target_user = get_object_or_404(User, pk=user_id)
        new_role = request.POST.get('role')
        if new_role in ('free', 'red', 'gold', 'admin'):
            profile, _ = Profile.objects.get_or_create(user=target_user)
            profile.role = new_role
            profile.save()
            messages.success(request, f"{target_user.username}'s role updated to {new_role}.")
        else:
            messages.error(request, 'Invalid role.')

    return redirect('register:admin_dashboard')


# ──────────────────────────────────────────────
# MEMBERSHIP PLANS
# ──────────────────────────────────────────────

MEMBERSHIP_PLANS = {
    'free': {
        'name':          'Free Member',
        'price':         0,
        'price_display': 'Free',
        'color':         '#6c757d',
        'benefits': [
            'Browse the full catalogue',
            'View match ratings',
            'View approved transfer rumours',
            'Basic profile page',
        ],
    },
    'red': {
        'name':          'Red Member',
        'price':         4.99,
        'price_display': '£4.99 / month',
        'color':         '#dc3545',
        'benefits': [
            'Everything in Free',
            'Submit transfer rumours',
            'Access to Red-exclusive products',
            'Red member badge on profile',
        ],
    },
    'gold': {
        'name':          'Gold Member',
        'price':         9.99,
        'price_display': '£9.99 / month',
        'color':         '#b8860b',
        'benefits': [
            'Everything in Red',
            '10% discount on all merchandise',
            'Gold Members Hub access',
            'Player of the Month voting',
            'Exclusive player & club stats',
            'Gold-exclusive products',
            'Gold member badge on profile',
        ],
    },
}


def membership_plans(request):
    current_role = 'free'
    if request.user.is_authenticated:
        try:
            current_role = request.user.profile.role
        except Exception:
            pass
    return render(request, 'register/membership_plans.html', {
        'plans':        MEMBERSHIP_PLANS,
        'current_role': current_role,
    })


@login_required
def membership_checkout(request, plan):
    if plan not in ('red', 'gold'):
        return redirect('register:membership_plans')

    plan_info    = MEMBERSHIP_PLANS[plan]
    current_role = 'free'
    try:
        current_role = request.user.profile.role
    except Exception:
        pass

    if current_role == 'admin':
        messages.info(request, 'As an admin you already have access to all membership benefits.')
        return redirect('register:membership_plans')

    tier_order = ['free', 'red', 'gold']
    if current_role in tier_order and tier_order.index(current_role) >= tier_order.index(plan):
        messages.info(request, f'You are already on {MEMBERSHIP_PLANS[current_role]["name"]} or higher.')
        return redirect('register:membership_plans')

    if request.method == 'POST':
        form = MembershipPaymentForm(request.POST)
        if form.is_valid():
            request.user.profile.role = plan
            request.user.profile.save()
            return redirect('register:membership_confirmation', plan=plan)
    else:
        form = MembershipPaymentForm()

    return render(request, 'register/membership_checkout.html', {
        'plan':      plan,
        'plan_info': plan_info,
        'form':      form,
    })


@login_required
def membership_confirmation(request, plan):
    plan_info = MEMBERSHIP_PLANS.get(plan, {})
    return render(request, 'register/membership_confirmation.html', {
        'plan':      plan,
        'plan_info': plan_info,
    })


# ──────────────────────────────────────────────
# PROFILE DASHBOARD
# ──────────────────────────────────────────────
@login_required(login_url='/login/')
def profile_dashboard(request):
    profile, created = Profile.objects.get_or_create(user=request.user)

    try:
        from catalogue.models import Product
        wishlist_count = request.user.wishlist_items.count() if hasattr(request.user, 'wishlist_items') else 0
    except Exception:
        wishlist_count = 0

    try:
        from catalogue.models import ProductRating
        ratings_count = ProductRating.objects.filter(user=request.user).count()
    except Exception:
        ratings_count = 0

    reviews_count = 0

    context = {
        'profile':        profile,
        'wishlist_count': wishlist_count,
        'ratings_count':  ratings_count,
        'reviews_count':  reviews_count,
    }
    return render(request, 'register/profile_dashboard.html', context)


# ──────────────────────────────────────────────
# EDIT PROFILE
# ──────────────────────────────────────────────
@login_required(login_url='/login/')
def edit_profile(request):
    profile, created = Profile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = EditProfileForm(request.POST, request.FILES, instance=profile, user=request.user)
        if form.is_valid():
            form.save()
            request.user.first_name = form.cleaned_data.get('first_name', '')
            request.user.last_name  = form.cleaned_data.get('last_name', '')
            request.user.email      = form.cleaned_data.get('email', request.user.email)
            request.user.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('register:profile_dashboard')
    else:
        form = EditProfileForm(instance=profile, user=request.user)

    return render(request, 'register/edit_profile.html', {'form': form})


# ──────────────────────────────────────────────
# CHANGE PASSWORD
# ──────────────────────────────────────────────
@login_required(login_url='/login/')
def change_password(request):
    if request.method == 'POST':
        form = StyledPasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            from django.contrib.auth import update_session_auth_hash
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Your password was updated successfully!')
            return redirect('register:change_password_done')
    else:
        form = StyledPasswordChangeForm(request.user)
    return render(request, 'register/change_password.html', {'form': form})


@login_required(login_url='/login/')
def change_password_done(request):
    return render(request, 'register/change_password_done.html')


def mark_message_read(request, pk):
    if not request.user.is_authenticated or not request.user.profile.is_admin():
        return redirect('core:home')
    from core.models import ContactMessage
    msg = get_object_or_404(ContactMessage, pk=pk)
    msg.is_read = True
    msg.save()
    return redirect('register:admin_dashboard')


def delete_message(request, pk):
    if not request.user.is_authenticated or not request.user.profile.is_admin():
        return redirect('core:home')
    from core.models import ContactMessage
    msg = get_object_or_404(ContactMessage, pk=pk)
    msg.delete()
    return redirect('register:admin_dashboard')

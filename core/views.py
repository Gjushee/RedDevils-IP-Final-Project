import re
from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse
from .models import ContactMessage


def home(request):
    return render(request, "core/home.html")


def about(request):
    return render(request, "core/about.html")


def contact(request):
    if request.method == 'POST':
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        name    = request.POST.get('name', '').strip()
        email   = request.POST.get('email', '').strip()
        subject = request.POST.get('subject', '').strip()
        msg     = request.POST.get('message', '').strip()

        errors = {}
        if len(name) < 3:
            errors['name'] = True
        if not re.match(r'^[^\s@]+@[^\s@]+\.[^\s@]+$', email):
            errors['email'] = True
        if len(subject) < 3:
            errors['subject'] = True
        words = msg.split()
        if len(msg) < 10 or len(words) > 200:
            errors['message'] = True

        if not errors:
            ContactMessage.objects.create(name=name, email=email, subject=subject, message=msg)
            if is_ajax:
                return JsonResponse({'success': True})
            messages.success(request, 'Thanks for your message!')
            return redirect('core:contact')
        else:
            if is_ajax:
                return JsonResponse({'success': False, 'errors': errors})
            messages.error(request, 'Please fix the errors below.')

    return render(request, "core/contact.html")

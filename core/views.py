import re
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import ContactMessage


def home(request):
    return render(request, "core/home.html")


def about(request):
    return render(request, "core/about.html")


def contact(request):
    if request.method == 'POST':
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        name         = request.POST.get('name', '').strip()
        email        = request.POST.get('email', '').strip()
        subject      = request.POST.get('subject', '').strip()
        message_text = request.POST.get('message', '').strip()

        errors = {}
        if len(name) < 3:
            errors['name'] = 'Name must be at least 3 characters.'
        if not re.match(r'^[^\s@]+@[^\s@]+\.[^\s@]+$', email):
            errors['email'] = 'Please enter a valid email address.'
        if len(subject) < 3:
            errors['subject'] = 'Subject must be at least 3 characters.'
        words = [w for w in message_text.split() if w]
        if len(message_text) < 10:
            errors['message'] = 'Message must be at least 10 characters.'
        elif len(words) > 200:
            errors['message'] = 'Message must not exceed 200 words.'

        if errors:
            if is_ajax:
                return JsonResponse({'success': False, 'errors': errors})
            return render(request, 'core/contact.html', {'errors': errors})

        ContactMessage.objects.create(
            name=name, email=email, subject=subject, message=message_text
        )

        if is_ajax:
            return JsonResponse({'success': True})
        return redirect('core:contact')

    return render(request, 'core/contact.html')


@require_POST
def mark_message_read(request, pk):
    msg = get_object_or_404(ContactMessage, pk=pk)
    msg.is_read = True
    msg.save()
    return redirect('register:admin_dashboard')

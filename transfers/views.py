from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Avg

from .models import TransferRumour
from .forms import TransferRumourForm
from register.decorators import red_member_required, admin_required


def transfers(request):
    rumours = TransferRumour.objects.filter(status='approved')

    position_filter = request.GET.get('position', '')
    sort_by = request.GET.get('sort', '-likelihood')

    if position_filter:
        rumours = rumours.filter(position=position_filter)

    valid_sorts = ['likelihood', '-likelihood', 'player_name', '-submitted_at']
    if sort_by not in valid_sorts:
        sort_by = '-likelihood'
    rumours = rumours.order_by(sort_by)

    total = TransferRumour.objects.filter(status='approved').count()
    very_likely = TransferRumour.objects.filter(status='approved', likelihood__gte=8).count()
    avg_likelihood = TransferRumour.objects.filter(status='approved').aggregate(
        avg=Avg('likelihood'))['avg'] or 0

    form = None
    can_submit = False
    if request.user.is_authenticated:
        profile = getattr(request.user, 'profile', None)
        can_submit = profile and profile.is_red_or_above()

    if can_submit:
        if request.method == 'POST':
            form = TransferRumourForm(request.POST)
            if form.is_valid():
                rumour = form.save(commit=False)
                rumour.submitted_by = request.user
                rumour.save()
                messages.success(request, "Rumour submitted — pending admin approval.")
                return redirect('transfers:transfers')
        else:
            form = TransferRumourForm()

    context = {
        'rumours': rumours, 'form': form, 'can_submit': can_submit,
        'position_filter': position_filter, 'sort_by': sort_by,
        'total': total, 'very_likely': very_likely,
        'avg_likelihood': round(avg_likelihood, 1),
    }
    return render(request, 'transfers/transfers.html', context)


@login_required
def my_rumours(request):
    profile = getattr(request.user, 'profile', None)
    if not profile or not profile.is_red_or_above():
        messages.warning(request, "Red or Gold membership required.")
        return redirect('transfers:transfers')
    rumours = TransferRumour.objects.filter(submitted_by=request.user)
    return render(request, 'transfers/my_rumours.html', {'rumours': rumours})


@login_required
def delete_rumour(request, pk):
    rumour = get_object_or_404(TransferRumour, pk=pk)
    profile = getattr(request.user, 'profile', None)
    if rumour.submitted_by != request.user and not (profile and profile.is_admin()):
        messages.error(request, "Permission denied.")
        return redirect('transfers:my_rumours')
    if request.method == 'POST':
        rumour.delete()
        messages.success(request, "Rumour deleted.")
        if profile and profile.is_admin():
            return redirect('transfers:admin_moderate')
        return redirect('transfers:my_rumours')
    return render(request, 'transfers/my_rumours.html', {'rumours': TransferRumour.objects.filter(submitted_by=request.user)})


@admin_required
def admin_moderate(request):
    pending = TransferRumour.objects.filter(status='pending')
    approved = TransferRumour.objects.filter(status='approved')
    rejected = TransferRumour.objects.filter(status='rejected')

    if request.method == 'POST':
        rumour_id = request.POST.get('rumour_id')
        action = request.POST.get('action')
        note = request.POST.get('admin_note', '')
        rumour = get_object_or_404(TransferRumour, pk=rumour_id)

        if action == 'approve':
            rumour.status = 'approved'
            rumour.admin_note = ''
            rumour.save()
            messages.success(request, f"Approved: {rumour.player_name}")
        elif action == 'reject':
            rumour.status = 'rejected'
            rumour.admin_note = note
            rumour.save()
            messages.warning(request, f"Rejected: {rumour.player_name}")
        elif action == 'delete':
            rumour.delete()
            messages.info(request, "Rumour deleted.")
        return redirect('transfers:admin_moderate')

    return render(request, 'transfers/admin_moderate.html', {
        'pending': pending, 'approved': approved, 'rejected': rejected
    })

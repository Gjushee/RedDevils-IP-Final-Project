from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import Poll, PollOption, Vote, PlayerStat, ClubStat
from .forms import PollForm, PollOptionForm, PlayerStatForm, ClubStatForm


def _admin_check(request):
    if not request.user.is_authenticated:
        messages.error(request, 'Please log in.')
        return redirect('register:login')
    try:
        if not request.user.profile.is_admin():
            messages.error(request, 'Access denied. Admin only.')
            return redirect('core:home')
    except Exception:
        return redirect('core:home')
    return None


def _is_gold(user):
    try:
        return user.profile.role in ('gold', 'admin')
    except Exception:
        return False


@login_required
def gold_hub(request):
    if not _is_gold(request.user):
        return render(request, 'gold_hub/locked.html')

    active_polls_qs = (
        Poll.objects.filter(is_active=True)
        .prefetch_related('options__votes')
        .order_by('-created_at')
    )

    polls_data = []
    for poll in active_polls_qs:
        try:
            user_vote       = Vote.objects.get(user=request.user, poll=poll)
            voted_option_id = user_vote.option_id
        except Vote.DoesNotExist:
            user_vote       = None
            voted_option_id = None

        total   = poll.total_votes
        options = []
        for opt in poll.options.all():
            options.append({
                'obj':        opt,
                'votes':      opt.vote_count,
                'percentage': opt.vote_percentage(total),
            })

        polls_data.append({
            'poll':            poll,
            'options':         options,
            'user_vote':       user_vote,
            'voted_option_id': voted_option_id,
        })

    player_stats = PlayerStat.objects.all()
    club_stat    = ClubStat.objects.filter(is_current=True).first()
    past_stats   = ClubStat.objects.filter(is_current=False)[:3]

    return render(request, 'gold_hub/gold_hub.html', {
        'polls_data':   polls_data,
        'player_stats': player_stats,
        'club_stat':    club_stat,
        'past_stats':   past_stats,
    })


@login_required
def cast_vote(request, option_id):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)

    if not _is_gold(request.user):
        return JsonResponse({'error': 'Gold membership required'}, status=403)

    option = get_object_or_404(PollOption, pk=option_id)
    poll   = option.poll

    if not poll.is_active:
        return JsonResponse({'error': 'This poll is closed'}, status=400)

    if Vote.objects.filter(user=request.user, poll=poll).exists():
        return JsonResponse({'error': 'You have already voted'}, status=400)

    Vote.objects.create(user=request.user, poll=poll, option=option)

    total   = poll.total_votes
    options = []
    for opt in poll.options.all():
        options.append({
            'id':         opt.id,
            'votes':      opt.vote_count,
            'percentage': opt.vote_percentage(total),
        })

    return JsonResponse({'ok': True, 'total': total, 'options': options, 'voted_id': option.id, 'poll_id': poll.id})


# ── ADMIN: Main overview 

def admin_gold_hub(request):
    guard = _admin_check(request)
    if guard:
        return guard
    polls        = Poll.objects.prefetch_related('options').order_by('-created_at')
    player_stats = PlayerStat.objects.all()
    club_stats   = ClubStat.objects.all()
    return render(request, 'gold_hub/admin/gold_hub_admin.html', {
        'polls': polls, 'player_stats': player_stats, 'club_stats': club_stats,
    })


# ── ADMIN: Polls 

def admin_poll_add(request):
    guard = _admin_check(request)
    if guard:
        return guard
    form = PollForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        poll = form.save()
        messages.success(request, f'Poll "{poll.title}" created.')
        return redirect('gold_hub:admin_poll_options', pk=poll.pk)
    return render(request, 'gold_hub/admin/poll_form.html', {'form': form, 'action': 'Add'})


def admin_poll_edit(request, pk):
    guard = _admin_check(request)
    if guard:
        return guard
    poll = get_object_or_404(Poll, pk=pk)
    form = PollForm(request.POST or None, instance=poll)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, f'Poll "{poll.title}" updated.')
        return redirect('gold_hub:admin_gold_hub')
    return render(request, 'gold_hub/admin/poll_form.html', {'form': form, 'poll': poll, 'action': 'Edit'})


def admin_poll_delete(request, pk):
    guard = _admin_check(request)
    if guard:
        return guard
    poll = get_object_or_404(Poll, pk=pk)
    if request.method == 'POST':
        poll.delete()
        messages.success(request, 'Poll deleted.')
        return redirect('gold_hub:admin_gold_hub')
    return render(request, 'gold_hub/admin/confirm_delete.html', {
        'title': f'Delete Poll: {poll.title}',
        'cancel_url': 'gold_hub:admin_gold_hub',
    })


# ── ADMIN: Poll Options 

def admin_poll_options(request, pk):
    guard = _admin_check(request)
    if guard:
        return guard
    poll    = get_object_or_404(Poll, pk=pk)
    options = poll.options.all()
    return render(request, 'gold_hub/admin/poll_options.html', {'poll': poll, 'options': options})


def admin_option_add(request, poll_pk):
    guard = _admin_check(request)
    if guard:
        return guard
    poll = get_object_or_404(Poll, pk=poll_pk)
    form = PollOptionForm(request.POST or None, request.FILES or None)
    if request.method == 'POST' and form.is_valid():
        opt = form.save(commit=False)
        opt.poll = poll
        opt.save()
        messages.success(request, f'Option "{opt.player_name}" added.')
        return redirect('gold_hub:admin_poll_options', pk=poll.pk)
    return render(request, 'gold_hub/admin/option_form.html', {'form': form, 'poll': poll, 'action': 'Add'})


def admin_option_edit(request, pk):
    guard = _admin_check(request)
    if guard:
        return guard
    opt  = get_object_or_404(PollOption, pk=pk)
    form = PollOptionForm(request.POST or None, request.FILES or None, instance=opt)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, f'Option "{opt.player_name}" updated.')
        return redirect('gold_hub:admin_poll_options', pk=opt.poll.pk)
    return render(request, 'gold_hub/admin/option_form.html', {'form': form, 'opt': opt, 'poll': opt.poll, 'action': 'Edit'})


def admin_option_delete(request, pk):
    guard = _admin_check(request)
    if guard:
        return guard
    opt = get_object_or_404(PollOption, pk=pk)
    poll_pk = opt.poll.pk
    if request.method == 'POST':
        opt.delete()
        messages.success(request, 'Option deleted.')
        return redirect('gold_hub:admin_poll_options', pk=poll_pk)
    return render(request, 'gold_hub/admin/confirm_delete.html', {
        'title': f'Delete Option: {opt.player_name}',
        'cancel_url': 'gold_hub:admin_gold_hub',
    })


# ── ADMIN: Player Stats 

def admin_player_stat_add(request):
    guard = _admin_check(request)
    if guard:
        return guard
    form = PlayerStatForm(request.POST or None, request.FILES or None)
    if request.method == 'POST' and form.is_valid():
        stat = form.save()
        messages.success(request, f'Player "{stat.name}" added.')
        return redirect('gold_hub:admin_gold_hub')
    return render(request, 'gold_hub/admin/player_stat_form.html', {'form': form, 'action': 'Add'})


def admin_player_stat_edit(request, pk):
    guard = _admin_check(request)
    if guard:
        return guard
    stat = get_object_or_404(PlayerStat, pk=pk)
    form = PlayerStatForm(request.POST or None, request.FILES or None, instance=stat)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, f'Player "{stat.name}" updated.')
        return redirect('gold_hub:admin_gold_hub')
    return render(request, 'gold_hub/admin/player_stat_form.html', {'form': form, 'stat': stat, 'action': 'Edit'})


def admin_player_stat_delete(request, pk):
    guard = _admin_check(request)
    if guard:
        return guard
    stat = get_object_or_404(PlayerStat, pk=pk)
    if request.method == 'POST':
        stat.delete()
        messages.success(request, 'Player stat deleted.')
        return redirect('gold_hub:admin_gold_hub')
    return render(request, 'gold_hub/admin/confirm_delete.html', {
        'title': f'Delete Player: {stat.name}',
        'cancel_url': 'gold_hub:admin_gold_hub',
    })


# ── ADMIN: Club Stats

def admin_club_stat_add(request):
    guard = _admin_check(request)
    if guard:
        return guard
    form = ClubStatForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        stat = form.save()
        messages.success(request, f'Club stat for {stat.season} added.')
        return redirect('gold_hub:admin_gold_hub')
    return render(request, 'gold_hub/admin/club_stat_form.html', {'form': form, 'action': 'Add'})


def admin_club_stat_edit(request, pk):
    guard = _admin_check(request)
    if guard:
        return guard
    stat = get_object_or_404(ClubStat, pk=pk)
    form = ClubStatForm(request.POST or None, instance=stat)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, f'Club stat for {stat.season} updated.')
        return redirect('gold_hub:admin_gold_hub')
    return render(request, 'gold_hub/admin/club_stat_form.html', {'form': form, 'stat': stat, 'action': 'Edit'})


def admin_club_stat_delete(request, pk):
    guard = _admin_check(request)
    if guard:
        return guard
    stat = get_object_or_404(ClubStat, pk=pk)
    if request.method == 'POST':
        stat.delete()
        messages.success(request, 'Club stat deleted.')
        return redirect('gold_hub:admin_gold_hub')
    return render(request, 'gold_hub/admin/confirm_delete.html', {
        'title': f'Delete Club Stat: {stat.season}',
        'cancel_url': 'gold_hub:admin_gold_hub',
    })

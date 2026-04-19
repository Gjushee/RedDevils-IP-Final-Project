from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import Poll, PollOption, Vote, PlayerStat, ClubStat


def _is_gold(user):
    try:
        return user.profile.role in ('gold', 'admin')
    except Exception:
        return False


@login_required
def gold_hub(request):
    if not _is_gold(request.user):
        return render(request, 'gold_hub/locked.html')

    active_poll = (
        Poll.objects.filter(is_active=True)
        .prefetch_related('options__votes')
        .first()
    )
    user_vote       = None
    voted_option_id = None
    if active_poll:
        try:
            user_vote       = Vote.objects.get(user=request.user, poll=active_poll)
            voted_option_id = user_vote.option_id
        except Vote.DoesNotExist:
            pass

    poll_options = []
    if active_poll:
        total = active_poll.total_votes
        for opt in active_poll.options.all():
            poll_options.append({
                'obj':        opt,
                'votes':      opt.vote_count,
                'percentage': opt.vote_percentage(total),
            })

    player_stats = PlayerStat.objects.all()
    club_stat    = ClubStat.objects.filter(is_current=True).first()
    past_stats   = ClubStat.objects.filter(is_current=False)[:3]

    return render(request, 'gold_hub/gold_hub.html', {
        'active_poll':     active_poll,
        'poll_options':    poll_options,
        'user_vote':       user_vote,
        'voted_option_id': voted_option_id,
        'player_stats':    player_stats,
        'club_stat':       club_stat,
        'past_stats':      past_stats,
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

    return JsonResponse({'ok': True, 'total': total, 'options': options, 'voted_id': option.id})

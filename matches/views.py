from django.shortcuts import render
from django.contrib.auth.decorators import login_required


@login_required
def match_ratings(request):
    return render(request, 'matches/match_ratings.html')

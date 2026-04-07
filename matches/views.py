from django.shortcuts import render
 
 
def match_ratings(request):
    return render(request, 'matches/match_ratings.html')
from django.urls import path
from . import views
 
app_name = 'matches'
 
urlpatterns = [
    path('match-ratings/', views.match_ratings, name='match_ratings'),
]
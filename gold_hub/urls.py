from django.urls import path
from . import views

app_name = 'gold_hub'

urlpatterns = [
    path('gold-hub/',                      views.gold_hub,  name='gold_hub'),
    path('gold-hub/vote/<int:option_id>/', views.cast_vote, name='cast_vote'),
]

from django.urls import path
from . import views

app_name = 'gold_hub'

urlpatterns = [
    path('gold-hub/',                          views.gold_hub,   name='gold_hub'),
    path('gold-hub/vote/<int:option_id>/',     views.cast_vote,  name='cast_vote'),

    # Admin
    path('manage/gold-hub/',                                views.admin_gold_hub,          name='admin_gold_hub'),
    path('manage/gold-hub/polls/add/',                      views.admin_poll_add,           name='admin_poll_add'),
    path('manage/gold-hub/polls/<int:pk>/edit/',            views.admin_poll_edit,          name='admin_poll_edit'),
    path('manage/gold-hub/polls/<int:pk>/delete/',          views.admin_poll_delete,        name='admin_poll_delete'),
    path('manage/gold-hub/polls/<int:pk>/options/',         views.admin_poll_options,       name='admin_poll_options'),
    path('manage/gold-hub/polls/<int:poll_pk>/options/add/',views.admin_option_add,         name='admin_option_add'),
    path('manage/gold-hub/options/<int:pk>/edit/',          views.admin_option_edit,        name='admin_option_edit'),
    path('manage/gold-hub/options/<int:pk>/delete/',        views.admin_option_delete,      name='admin_option_delete'),
    path('manage/gold-hub/players/add/',                    views.admin_player_stat_add,    name='admin_player_stat_add'),
    path('manage/gold-hub/players/<int:pk>/edit/',          views.admin_player_stat_edit,   name='admin_player_stat_edit'),
    path('manage/gold-hub/players/<int:pk>/delete/',        views.admin_player_stat_delete, name='admin_player_stat_delete'),
    path('manage/gold-hub/clubs/add/',                      views.admin_club_stat_add,      name='admin_club_stat_add'),
    path('manage/gold-hub/clubs/<int:pk>/edit/',            views.admin_club_stat_edit,     name='admin_club_stat_edit'),
    path('manage/gold-hub/clubs/<int:pk>/delete/',          views.admin_club_stat_delete,   name='admin_club_stat_delete'),
]

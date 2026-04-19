from django.contrib import admin
from .models import Poll, PollOption, Vote, PlayerStat, ClubStat


class PollOptionInline(admin.TabularInline):
    model = PollOption
    extra = 3


@admin.register(Poll)
class PollAdmin(admin.ModelAdmin):
    list_display = ('title', 'month_label', 'is_active', 'total_votes', 'created_at')
    list_filter  = ('is_active',)
    inlines      = [PollOptionInline]


@admin.register(Vote)
class VoteAdmin(admin.ModelAdmin):
    list_display = ('user', 'poll', 'option', 'created_at')
    list_filter  = ('poll',)


@admin.register(PlayerStat)
class PlayerStatAdmin(admin.ModelAdmin):
    list_display  = ('name', 'position', 'season', 'appearances', 'goals', 'assists', 'rating')
    list_filter   = ('position', 'season')
    list_editable = ('appearances', 'goals', 'assists', 'rating')


@admin.register(ClubStat)
class ClubStatAdmin(admin.ModelAdmin):
    list_display  = ('season', 'competition', 'position', 'played', 'won', 'drawn', 'lost', 'points', 'is_current')
    list_editable = ('is_current',)

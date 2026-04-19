from django.db import models
from django.contrib.auth.models import User


class Poll(models.Model):
    title       = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    month_label = models.CharField(max_length=50, help_text='e.g. April 2025')
    is_active   = models.BooleanField(default=True)
    created_at  = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    @property
    def total_votes(self):
        return self.votes.count()


class PollOption(models.Model):
    poll        = models.ForeignKey(Poll, on_delete=models.CASCADE, related_name='options')
    player_name = models.CharField(max_length=100)
    description = models.CharField(max_length=200, blank=True, help_text='e.g. 3 goals vs Arsenal')
    image       = models.ImageField(upload_to='poll_players/', blank=True)
    order       = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', 'player_name']

    def __str__(self):
        return f'{self.player_name} ({self.poll})'

    @property
    def vote_count(self):
        return self.votes.count()

    def vote_percentage(self, total):
        if not total:
            return 0
        return round(self.votes.count() / total * 100)


class Vote(models.Model):
    user       = models.ForeignKey(User, on_delete=models.CASCADE, related_name='gold_votes')
    poll       = models.ForeignKey(Poll, on_delete=models.CASCADE, related_name='votes')
    option     = models.ForeignKey(PollOption, on_delete=models.CASCADE, related_name='votes')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'poll')

    def __str__(self):
        return f'{self.user.username} → {self.option.player_name}'


class PlayerStat(models.Model):
    POSITION_CHOICES = [
        ('GK',  'Goalkeeper'),
        ('DEF', 'Defender'),
        ('MID', 'Midfielder'),
        ('FWD', 'Forward'),
    ]

    name         = models.CharField(max_length=100)
    position     = models.CharField(max_length=3, choices=POSITION_CHOICES)
    image        = models.ImageField(upload_to='player_stats/', blank=True)
    season       = models.CharField(max_length=10, default='2024/25')
    appearances  = models.PositiveIntegerField(default=0)
    goals        = models.PositiveIntegerField(default=0)
    assists      = models.PositiveIntegerField(default=0)
    clean_sheets = models.PositiveIntegerField(default=0, help_text='GK/DEF only')
    rating       = models.DecimalField(max_digits=3, decimal_places=1, default=0.0)
    order        = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', 'name']

    def __str__(self):
        return f'{self.name} ({self.season})'


class ClubStat(models.Model):
    season        = models.CharField(max_length=10)
    competition   = models.CharField(max_length=100, default='Premier League')
    played        = models.PositiveIntegerField(default=0)
    won           = models.PositiveIntegerField(default=0)
    drawn         = models.PositiveIntegerField(default=0)
    lost          = models.PositiveIntegerField(default=0)
    goals_for     = models.PositiveIntegerField(default=0)
    goals_against = models.PositiveIntegerField(default=0)
    position      = models.PositiveIntegerField(default=0)
    points        = models.PositiveIntegerField(default=0)
    is_current    = models.BooleanField(default=False)

    class Meta:
        ordering = ['-season']

    def __str__(self):
        return f'{self.season} — {self.competition}'

    @property
    def goal_difference(self):
        return self.goals_for - self.goals_against

    @property
    def win_rate(self):
        if not self.played:
            return 0
        return round(self.won / self.played * 100)
        
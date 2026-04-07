from django.db import models
from django.contrib.auth.models import User


class TransferRumour(models.Model):
    POSITION_CHOICES = [
        ('GK', 'Goalkeeper'),
        ('DEF', 'Defender'),
        ('MID', 'Midfielder'),
        ('FWD', 'Forward'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    submitted_by = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='transfer_rumours'
    )
    player_name = models.CharField(max_length=100)
    current_club = models.CharField(max_length=100)
    position = models.CharField(max_length=3, choices=POSITION_CHOICES)
    age = models.PositiveIntegerField()
    fee = models.CharField(max_length=50)
    source = models.URLField(blank=True)
    likelihood = models.PositiveIntegerField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    admin_note = models.TextField(blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-submitted_at']

    def __str__(self):
        return f"{self.player_name} ({self.current_club}) — {self.get_status_display()}"

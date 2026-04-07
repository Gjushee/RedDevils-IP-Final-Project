import uuid
from django.db import models
from django.contrib.auth.models import User

 
 
class Profile(models.Model):
    ROLE_CHOICES = [
        ('free',  'Free'),
        ('red',   'Red Member'),
        ('gold',  'Gold Member'),
        ('admin', 'Admin'),
    ]
 
    user               = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role               = models.CharField(max_length=10, choices=ROLE_CHOICES, default='free')
    full_name          = models.CharField(max_length=100, blank=True)
    bio                = models.TextField(blank=True)
    profile_image      = models.ImageField(upload_to='profiles/', blank=True, null=True)
    favourite_player   = models.CharField(max_length=100, blank=True)
    date_of_birth      = models.DateField(null=True, blank=True)
    phone_number       = models.CharField(max_length=20, blank=True)
    email_verified     = models.BooleanField(default=False)
    verification_token = models.CharField(max_length=100, blank=True, unique=True)
    created_at         = models.DateTimeField(auto_now_add=True)
 
    def __str__(self):
        return f"{self.user.username} ({self.get_role_display()})"
 
    def is_admin(self):
        return self.role == 'admin'
 
    def is_red_or_above(self):
        return self.role in ('red', 'gold', 'admin')
 
    def is_gold_or_above(self):
        return self.role in ('gold', 'admin')
 
    def save(self, *args, **kwargs):
        # Auto-generate a verification token if not set
        if not self.verification_token:
            self.verification_token = str(uuid.uuid4())
        super().save(*args, **kwargs)
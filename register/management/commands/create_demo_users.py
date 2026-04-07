from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from register.models import Profile
 
 
DEMO_USERS = [
    {
        'username':        'demo_free',
        'email':           'demo_free@reddevilshub.com',
        'password':        'DemoFree123',
        'full_name':       'Demo Free User',
        'favourite_player': 'Marcus Rashford',
        'bio':             'Free tier demo account. Can browse, rate players, and manage a wishlist.',
        'role':            'free',
    },
    {
        'username':        'demo_red',
        'email':           'demo_red@reddevilshub.com',
        'password':        'DemoRed123',
        'full_name':       'Demo Red Member',
        'favourite_player': 'Bruno Fernandes',
        'bio':             'Red membership demo account. Can submit transfer rumours and access member discounts.',
        'role':            'red',
    },
    {
        'username':        'demo_gold',
        'email':           'demo_gold@reddevilshub.com',
        'password':        'DemoGold123',
        'full_name':       'Demo Gold Member',
        'favourite_player': 'Kobbie Mainoo',
        'bio':             'Gold membership demo account. Full access including premium player analysis and early products.',
        'role':            'gold',
    },
]
 
 
class Command(BaseCommand):
    help = 'Creates three demo users representing Free, Red, and Gold membership tiers'
 
    def handle(self, *args, **kwargs):
        for data in DEMO_USERS:
            user, created = User.objects.get_or_create(
                username=data['username'],
                defaults={'email': data['email']}
            )
 
            if created:
                user.set_password(data['password'])
                user.save()
                self.stdout.write(f"  Created user: {data['username']}")
            else:
                self.stdout.write(f"  User already exists: {data['username']} (skipped)")
 
            # Create or update the profile
            profile, _ = Profile.objects.get_or_create(user=user)
            profile.role             = data['role']
            profile.full_name        = data['full_name']
            profile.favourite_player = data['favourite_player']
            profile.bio              = data['bio']
            profile.email_verified   = True   # Pre-verified so they can log in immediately
            profile.save()
 
            self.stdout.write(
                self.style.SUCCESS(f"  Profile set — {data['username']} ({data['role'].upper()})")
            )
 
        self.stdout.write(self.style.SUCCESS('\nDemo users ready:'))
        self.stdout.write('  Username: demo_free   | Password: DemoFree123 | Role: Free')
        self.stdout.write('  Username: demo_red    | Password: DemoRed123  | Role: Red Member')
        self.stdout.write('  Username: demo_gold   | Password: DemoGold123 | Role: Gold Member')
"""
Load demo passport stamps and sample destinations for impressive demos.
Usage: python manage.py load_demo_data [--user USERNAME]
"""

from datetime import date, timedelta

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from social.gamification import CONTINENT_BY_COUNTRY
from social.models import BucketList, PassportStamp, Post


DEMO_STAMPS = [
    ('Kyoto', 'Kansai', 'Japan', 'Asia', 'Temple & culture trail'),
    ('Reykjavik', '', 'Iceland', 'Europe', 'Northern lights quest'),
    ('Amalfi', 'Campania', 'Italy', 'Europe', 'Coastal road trip'),
    ('Cusco', '', 'Peru', 'South America', 'Machu Picchu gateway'),
    ('Sydney', 'NSW', 'Australia', 'Oceania', 'Harbour & beaches'),
    ('Marrakech', '', 'Morocco', 'Africa', 'Medina explorer'),
    ('Banff', 'Alberta', 'Canada', 'North America', 'Rocky mountains'),
    ('Santorini', '', 'Greece', 'Europe', 'Sunset villages'),
]

DEMO_BUCKET = [
    ('Bali Rice Terraces', 'high', 'Relaxation & photography', 20),
    ('Patagonia W Trek', 'high', 'Adventure hiking', 10),
    ('Santorini Caldera', 'medium', 'Honeymoon-style getaway', 40),
    ('Kyoto Autumn', 'medium', 'Temple hopping', 60),
]


class Command(BaseCommand):
    help = 'Load demo passport stamps and bucket list items for testing/demo'

    def add_arguments(self, parser):
        parser.add_argument('--user', type=str, default='', help='Username (default: first user)')

    def handle(self, *args, **options):
        username = options['user']
        if username:
            user = User.objects.filter(username=username).first()
        else:
            user = User.objects.first()
        if not user:
            self.stdout.write(self.style.ERROR('No user found. Create a user first (register or createsuperuser).'))
            return

        created_stamps = 0
        for city, state, country, continent, label in DEMO_STAMPS:
            _, created = PassportStamp.objects.get_or_create(
                user=user,
                country=country,
                city=city,
                defaults={
                    'state': state,
                    'continent': continent or CONTINENT_BY_COUNTRY.get(country, ''),
                    'stamp_label': label,
                    'visited_at': date.today() - timedelta(days=created_stamps * 45),
                },
            )
            if created:
                created_stamps += 1

        created_bucket = 0
        for dest, priority, goal, progress in DEMO_BUCKET:
            _, created = BucketList.objects.get_or_create(
                user=user,
                destination_name=dest,
                defaults={
                    'priority': priority,
                    'travel_goal': goal,
                    'progress': progress,
                    'status': 'planned' if progress < 50 else 'in_progress',
                },
            )
            if created:
                created_bucket += 1

        user.profile.recalculate_explorer_score()
        from social.services import update_post_gem_score
        for post in Post.objects.all():
            update_post_gem_score(post)

        self.stdout.write(self.style.SUCCESS(
            f'Demo data for @{user.username}: {created_stamps} new stamps, {created_bucket} bucket items.'
        ))

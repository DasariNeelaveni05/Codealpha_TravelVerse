"""Recalculate explorer scores and hidden gem scores for all users/posts."""

from django.core.management.base import BaseCommand

from django.contrib.auth.models import User
from social.models import Post, Profile
from social.services import update_post_gem_score


class Command(BaseCommand):
    help = 'Recalculate hidden gem scores and explorer XP for all content'

    def handle(self, *args, **options):
        self.stdout.write('🔄 Recalculating hidden gem scores for posts...')
        for post in Post.objects.all():
            update_post_gem_score(post)
        
        self.stdout.write('✨ Updating explorer scores for all users...')
        for user in User.objects.all():
            # Ensure profile exists before updating
            profile, created = Profile.objects.get_or_create(user=user)
            new_score = profile.recalculate_explorer_score()
            if options.get('verbosity', 1) >= 2:
                self.stdout.write(f'  - {user.username}: {new_score} XP')

        self.stdout.write(self.style.SUCCESS('Scores recalculated.'))

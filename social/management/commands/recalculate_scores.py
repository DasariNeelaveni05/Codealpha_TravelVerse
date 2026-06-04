"""Recalculate explorer scores and hidden gem scores for all users/posts."""

from django.core.management.base import BaseCommand

from social.models import Post, User
from social.services import update_post_gem_score


class Command(BaseCommand):
    help = 'Recalculate hidden gem scores and explorer XP for all content'

    def handle(self, *args, **options):
        for post in Post.objects.all():
            update_post_gem_score(post)
        for user in User.objects.all():
            if hasattr(user, 'profile'):
                user.profile.recalculate_explorer_score()
        self.stdout.write(self.style.SUCCESS('Scores recalculated.'))

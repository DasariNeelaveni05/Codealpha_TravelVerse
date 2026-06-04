import logging
import random

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.utils.text import slugify

from social.models import Post, Reel, Profile, Comment, Like, Follow

logger = logging.getLogger(__name__)

SAMPLE_FIRST = ['Ava','Liam','Noah','Olivia','Emma','Oliver','Sophia','Mia','Lucas','Amelia']
SAMPLE_LAST = ['Walker','Singh','Patel','Garcia','Kim','Nguyen','Brown','Wilson','Martin','Lee']
SAMPLE_LOCATIONS = ['Iguazu Falls, Argentina','Plitvice Lakes, Croatia','Havasu Falls, USA','Goa Waterfalls, India','Seljalandsfoss, Iceland','Kuang Si Falls, Laos']
SAMPLE_IMAGES = [
    'https://images.unsplash.com/photo-1501785888041-af3ef285b470?auto=format&fit=crop&w=800&q=60',
    'https://images.unsplash.com/photo-1502082553048-f009c37129b9?auto=format&fit=crop&w=800&q=60',
    'https://images.unsplash.com/photo-1505577058444-a3dab1b5f3d6?auto=format&fit=crop&w=800&q=60',
]
SAMPLE_CAPTIONS = [
    'A hidden waterfall I stumbled upon — pure magic.',
    'Chasing waterfalls and good vibes.',
    'Secret pools and mossy trails. Worth the hike!',
    'Sunlight and mist — a perfect travel memory.'
]


class Command(BaseCommand):
    help = 'Generate fake users, posts, and reels for UI preview.'

    def add_arguments(self, parser):
        parser.add_argument('--users', type=int, default=6, help='Number of fake users to create')
        parser.add_argument('--posts', type=int, default=4, help='Posts per user')
        parser.add_argument('--reels', type=int, default=2, help='Reels per user')

    def handle(self, *args, **options):
        users = options['users']
        posts_per = options['posts']
        reels_per = options['reels']

        created_users = []
        for i in range(users):
            first = random.choice(SAMPLE_FIRST)
            last = random.choice(SAMPLE_LAST)
            username = slugify(f"{first}-{last}-{random.randint(10,999)}")[:30]
            if User.objects.filter(username=username).exists():
                user = User.objects.filter(username=username).first()
            else:
                user = User.objects.create_user(username=username, email=f"{username}@example.com", password='password123')
                user.first_name = first
                user.last_name = last
                user.save()
            # ensure profile exists
            Profile.objects.get_or_create(user=user, defaults={'avatar_url': f'https://i.pravatar.cc/150?u={username}'})
            created_users.append(user)

        created_posts = 0
        created_reels = 0
        for user in created_users:
            for p in range(posts_per):
                loc = random.choice(SAMPLE_LOCATIONS)
                caption = random.choice(SAMPLE_CAPTIONS)
                img = random.choice(SAMPLE_IMAGES)
                post = Post.objects.create(
                    author=user,
                    caption=caption,
                    image_url=img,
                    location=loc,
                )
                created_posts += 1
                # add a like from a random other user
                other = random.choice(created_users)
                if other != user:
                    try:
                        Like.objects.create(user=other, post=post)
                    except IntegrityError:
                        pass  # duplicate like, expected
                    except Exception:
                        logger.warning('Failed to create demo like for post %d', post.pk, exc_info=True)

            for r in range(reels_per):
                thumb = random.choice(SAMPLE_IMAGES)
                reel = Reel.objects.create(
                    author=user,
                    title='Short waterfall clip',
                    thumbnail_url=thumb,
                    caption=random.choice(SAMPLE_CAPTIONS),
                    location=random.choice(SAMPLE_LOCATIONS),
                )
                created_reels += 1

        # Create some follows among users
        for a in created_users:
            others = [u for u in created_users if u != a]
            for followee in random.sample(others, min(3, len(others))):
                try:
                    Follow.objects.create(follower=a, following=followee)
                except IntegrityError:
                    pass  # duplicate follow, expected
                except Exception:
                    logger.warning('Failed to create demo follow %s -> %s', a.username, followee.username, exc_info=True)

        self.stdout.write(self.style.SUCCESS(
            f'Generated {len(created_users)} users, {created_posts} posts, {created_reels} reels.'
        ))

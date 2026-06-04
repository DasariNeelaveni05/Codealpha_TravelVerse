from django.test import TestCase
from django.contrib.auth import get_user_model
from .models import Profile, Post, PassportStamp, Like

User = get_user_model()

class TravelVerseTestCase(TestCase):
    def setUp(self):
        # Create users
        self.user1 = User.objects.create_user(username='alice', password='password123')
        self.user2 = User.objects.create_user(username='bob', password='password123')
        
    def test_profile_creation_signal(self):
        """Test that a Profile is automatically created when a User is created."""
        self.assertTrue(Profile.objects.filter(user=self.user1).exists())
        profile = self.user1.profile
        self.assertEqual(profile.explorer_score, 0)
        self.assertEqual(profile.badge, 'Explorer')

    def test_post_creation_and_recalculation(self):
        """Test creating a post and calculating the explorer score."""
        profile = self.user1.profile
        post = Post.objects.create(
            author=self.user1,
            caption="Exploring the beautiful beaches of Bali",
            location="Bali, Indonesia",
            country="Indonesia",
            is_hidden_gem=True,
            hidden_gem_score=80
        )
        
        # Recalculate explorer score
        score = profile.recalculate_explorer_score()
        self.assertEqual(score, 15) # 15 points per post

    def test_passport_stamp(self):
        """Test passport stamp recording for country visits."""
        PassportStamp.objects.create(
            user=self.user1,
            country="Indonesia",
            city="Denpasar",
            stamp_label="Bali Trip"
        )
        stamps = self.user1.passport_stamps.all()
        self.assertEqual(stamps.count(), 1)
        self.assertEqual(stamps.first().country, "Indonesia")

    def test_like_and_engagement(self):
        """Test like action on a post."""
        post = Post.objects.create(
            author=self.user1,
            caption="Stunning view",
            location="Paris, France",
            country="France"
        )
        
        # Bob likes Alice's post
        Like.objects.create(user=self.user2, post=post)
        
        # Check like count
        self.assertEqual(post.like_count, 1)
        self.assertTrue(Like.objects.filter(user=self.user2, post=post).exists())

    def test_feed_category_filter(self):
        """Feed should filter posts by the ?category= query param."""
        from .views import _feed_posts
        beach = Post.objects.create(
            author=self.user1, caption="Bali beach", location="Bali",
            country="Indonesia", category="beach", is_hidden_gem=True,
        )
        Post.objects.create(
            author=self.user1, caption="Alps peak", location="Alps",
            country="Switzerland", category="mountain", is_hidden_gem=True,
        )

        all_posts = list(_feed_posts(self.user2, page=1))
        self.assertEqual(len(all_posts), 2)

        beaches = list(_feed_posts(self.user2, page=1, category="beach"))
        self.assertEqual([p.pk for p in beaches], [beach.pk])

        # Unknown category is ignored (returns everything)
        bogus = list(_feed_posts(self.user2, page=1, category="not-a-real-cat"))
        self.assertEqual(len(bogus), 2)

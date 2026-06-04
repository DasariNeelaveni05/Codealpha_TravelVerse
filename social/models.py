from django.conf import settings
from django.contrib.auth.models import User
from django.db import models


# Existing imports remain.
from django.db.models import Count, Q
from django.urls import reverse

from .gamification import badge_tier_for_score, explorer_progress
from .utils import explorer_badge


class Profile(models.Model):

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    avatar_url = models.URLField(blank=True)
    bio = models.TextField(blank=True, max_length=300)
    location = models.CharField(max_length=150, blank=True)
    website = models.URLField(blank=True)
    explorer_score = models.PositiveIntegerField(default=0)
    countries_visited = models.TextField(blank=True, default='[]')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def badge(self):
        return explorer_badge(self.explorer_score)

    @property
    def badge_full_name(self):
        return badge_tier_for_score(self.explorer_score)[2]

    @property
    def badge_icon(self):
        return badge_tier_for_score(self.explorer_score)[3]

    @property
    def badge_slug(self):
        return badge_tier_for_score(self.explorer_score)[1]

    @property
    def explorer_progress(self):
        return explorer_progress(self.explorer_score)

    @property
    def followers_count(self):
        return self.user.followers_set.count()

    @property
    def following_count(self):
        return self.user.following_set.count()

    @property
    def posts_count(self):
        return self.user.posts.count()

    def add_score(self, points):
        self.explorer_score += points
        self.save(update_fields=['explorer_score', 'updated_at'])

    def get_avatar(self):
        if self.avatar:
            return self.avatar.url
        if self.avatar_url:
            return self.avatar_url
        return 'https://i.pravatar.cc/150?u=' + self.user.username

    def get_badge(self):
        if self.explorer_score >= 10000:
            return ('Platinum', '🥇')
        if self.explorer_score >= 5000:
            return ('Gold', '🏅')
        if self.explorer_score >= 2000:
            return ('Silver', '🥈')
        return ('Bronze', '🥉')

    def recalculate_explorer_score(self):
        """Gamification score from posts, engagement, followers, and travel activity."""
        user = self.user
        received_likes = Like.objects.filter(post__author=user).count()
        gem_votes = HiddenGemVote.objects.filter(post__author=user).count()
        followers = Follow.objects.filter(following=user).count()
        score = (
            user.posts.count() * 15
            + user.reels.count() * 20
            + user.blogs.count() * 25
            + received_likes * 2
            + followers * 5
            + gem_votes * 3
            + user.passport_stamps.count() * 8
        )
        self.explorer_score = score
        self.save(update_fields=['explorer_score', 'updated_at'])
        return score

    def __str__(self):
        return f"{self.user.username}'s profile"


class UserProfile(Profile):
    class Meta:
        proxy = True
        verbose_name = 'User Profile'
        verbose_name_plural = 'User Profiles'


class Post(models.Model):
    CATEGORY_CHOICES = [
        ('beach', 'Beaches'),
        ('mountain', 'Mountains'),
        ('adventure', 'Adventure'),
        ('historical', 'Historical Places'),
        ('food', 'Food Destinations'),
        ('nature', 'Nature'),
        ('island', 'Islands'),
        ('budget', 'Budget Travel'),
        ('city', 'City'),
        ('forest', 'Forest'),
        ('desert', 'Desert'),
        ('cultural', 'Cultural'),
        ('other', 'Other'),
    ]
    DIFFICULTY_CHOICES = [
        ('easy', 'Easy'),
        ('moderate', 'Moderate'),
        ('hard', 'Hard'),
        ('expert', 'Expert'),
    ]
    CROWD_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    ]

    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    caption = models.TextField(blank=True, max_length=2200)
    image = models.ImageField(upload_to='posts/', blank=True, null=True)
    image_url = models.URLField(blank=True)
    location = models.CharField(max_length=200)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, blank=True)
    budget = models.CharField(max_length=100, blank=True)
    best_season = models.CharField(max_length=100, blank=True)
    safety_rating = models.PositiveSmallIntegerField(default=5)
    crowd_level = models.CharField(max_length=20, choices=CROWD_CHOICES, default='medium')
    difficulty = models.CharField(max_length=20, choices=DIFFICULTY_CHOICES, default='moderate')
    category = models.CharField(max_length=30, choices=CATEGORY_CHOICES, default='other')
    itinerary = models.TextField(blank=True)
    travel_tips = models.TextField(blank=True)
    hidden_gem_description = models.TextField(
        blank=True,
        max_length=1500,
        help_text='Why is this place a hidden gem?',
    )
    is_hidden_gem = models.BooleanField(default=False)
    gem_votes = models.PositiveIntegerField(default=0)
    hidden_gem_score = models.PositiveSmallIntegerField(default=0, help_text='0-100 community gem score')
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    budget_amount = models.PositiveIntegerField(null=True, blank=True, help_text='Trip budget in USD')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Post by {self.author.username} at {self.location}"

    def get_absolute_url(self):
        return reverse('post_detail', kwargs={'pk': self.pk})

    @property
    def like_count(self):
        return self.likes.count()

    @property
    def comment_count(self):
        return self.comments.filter(parent__isnull=True).count()

    @property
    def primary_image(self):
        first = self.images.first()
        return first.image if first else None
    def get_image(self):
        if self.image:
            return self.image.url
        return self.image_url or ''
    @property
    def save_count(self):
        return self.saved_by.count()

    @property
    def is_certified_gem(self):
        return self.is_hidden_gem and self.gem_votes >= 3 and self.hidden_gem_score >= 35


class PostImage(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='posts/')
    order = models.PositiveSmallIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order', 'id']


class Reel(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reels')
    title = models.CharField(max_length=200, blank=True)
    video = models.FileField(upload_to='reels/', blank=True, null=True)
    video_url = models.URLField(blank=True, null=True)
    audio_url = models.URLField(blank=True, null=True)
    thumbnail = models.ImageField(upload_to='reels/thumbs/', blank=True, null=True)
    thumbnail_url = models.URLField(blank=True)
    caption = models.TextField(blank=True, max_length=500)
    location = models.CharField(max_length=200, blank=True)
    country = models.CharField(max_length=100, blank=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    @property
    def like_count(self):
        return self.reel_likes.count()
    
    @property
    def display_thumbnail(self):
        if self.thumbnail:
            return self.thumbnail.url
        return self.thumbnail_url or ''


class Blog(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='blogs')
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True)
    content = models.TextField()
    cover_image = models.ImageField(upload_to='blogs/', blank=True, null=True)
    location = models.CharField(max_length=200, blank=True)
    budget = models.CharField(max_length=120, blank=True)
    itinerary = models.TextField(blank=True)
    recommendations = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments', null=True, blank=True)
    reel = models.ForeignKey(Reel, on_delete=models.CASCADE, related_name='comments', null=True, blank=True)
    blog = models.ForeignKey(Blog, on_delete=models.CASCADE, related_name='comments', null=True, blank=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')
    text = models.TextField(max_length=1000)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    @property
    def author(self):
        return self.user


class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='post_likes')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='likes')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'post')


class ReelLike(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reel_likes')
    reel = models.ForeignKey(Reel, on_delete=models.CASCADE, related_name='reel_likes')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'reel')


class Follow(models.Model):
    follower = models.ForeignKey(User, on_delete=models.CASCADE, related_name='following_set')
    following = models.ForeignKey(User, on_delete=models.CASCADE, related_name='followers_set')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('follower', 'following')


class BucketList(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bucket_list')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='bucket_entries', null=True, blank=True)
    destination_name = models.CharField(max_length=200)
    notes = models.TextField(blank=True)
    planned_date = models.DateField(null=True, blank=True, help_text='When you plan to visit')
    priority = models.CharField(
        max_length=20,
        choices=[('low', 'Low'), ('medium', 'Medium'), ('high', 'High')],
        default='medium',
        blank=True,
    )
    travel_goal = models.CharField(max_length=255, blank=True)
    progress = models.PositiveSmallIntegerField(default=0, help_text='0-100 planning progress')
    status = models.CharField(
        max_length=20,
        choices=[
            ('planned', 'Planned'),
            ('in_progress', 'In Progress'),
            ('visited', 'Visited'),
        ],
        default='planned',
    )
    reminder_date = models.DateField(null=True, blank=True)
    cover_theme = models.CharField(max_length=30, blank=True, help_text='Placeholder image theme key')
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'destination_name')
        ordering = ['-added_at']


class TravelCompanion(models.Model):
    """Users looking for travel partners by destination and dates."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='companion_trips')
    destination = models.CharField(max_length=200)
    country = models.CharField(max_length=100, blank=True)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    description = models.TextField(max_length=800, blank=True)
    budget_range = models.CharField(max_length=80, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} → {self.destination}"


class SavedPost(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='saved_posts')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='saved_by')
    saved_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'post')


class HiddenGemVote(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='gem_votes')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='votes')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'post')


class PassportStamp(models.Model):
    CONTINENT_CHOICES = [
        ('', 'Unknown'),
        ('Africa', 'Africa'),
        ('Asia', 'Asia'),
        ('Europe', 'Europe'),
        ('North America', 'North America'),
        ('South America', 'South America'),
        ('Oceania', 'Oceania'),
        ('Antarctica', 'Antarctica'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='passport_stamps')
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100)
    continent = models.CharField(max_length=30, choices=CONTINENT_CHOICES, blank=True, default='')
    visited_at = models.DateField(null=True, blank=True)
    post = models.ForeignKey(Post, on_delete=models.SET_NULL, null=True, blank=True)
    stamp_label = models.CharField(max_length=120, blank=True, help_text='Passport stamp title')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-visited_at', '-created_at']


class UserAchievement(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='achievements')
    key = models.CharField(max_length=50)
    unlocked_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'key')


class Notification(models.Model):
    NOTIFICATION_TYPES = [
        ('like', 'Like'),
        ('comment', 'Comment'),
        ('follow', 'Follow'),
        ('reply', 'Reply'),
        ('gem_vote', 'Hidden Gem Vote'),
    ]
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    actor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_notifications')
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    message = models.CharField(max_length=255)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, null=True, blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']


# ── NEW MODELS ──────────────────────────────────────────────────

class GuideProfile(models.Model):
    """Local guide who can be discovered and contacted by first-time visitors."""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='guide_profile')
    destinations = models.TextField(blank=True, help_text='Comma-separated cities')
    destination_expertise = models.TextField(
        help_text='JSON list of cities, e.g. ["Ooty","Kodaikanal"]', blank=True, default='[]'
    )
    languages = models.CharField(max_length=200, blank=True, default='English')
    experience_years = models.PositiveSmallIntegerField(default=1)
    price_per_day = models.DecimalField(max_digits=8, decimal_places=2, default=1500)
    rating = models.FloatField(default=5.0)
    total_tours = models.PositiveIntegerField(default=0)
    bio = models.TextField(blank=True)
    is_verified = models.BooleanField(default=False)
    is_available = models.BooleanField(default=True)
    whatsapp_number = models.CharField(max_length=20, blank=True)
    profile_image_url = models.URLField(blank=True)
    speciality = models.CharField(max_length=200, blank=True)
    certifications = models.TextField(blank=True)
    availability_status = models.BooleanField(default=True)
    response_time = models.CharField(max_length=60, default='Within an hour')
    phone = models.CharField(max_length=20, blank=True)
    whatsapp = models.CharField(max_length=20, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-rating', '-total_tours']

    class Meta:
        ordering = ['-rating', '-total_tours']

    def __str__(self):
        return f"Guide: {self.user.username}"

    @property
    def expertise_cities(self):
        import json
        try:
            return json.loads(self.destination_expertise)
        except Exception:
            return []


class GuideRequest(models.Model):
    """User posting a guide-needed request for a destination."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='guide_requests')
    destination = models.CharField(max_length=200)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    group_size = models.PositiveSmallIntegerField(default=1)
    budget = models.CharField(max_length=80, blank=True)
    is_open = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} → {self.destination}"


class Destination(models.Model):
    """Rich destination metadata used for first-timer guide widgets."""
    name = models.CharField(max_length=200, unique=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, blank=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    description = models.TextField(blank=True)
    best_time = models.CharField(max_length=200, blank=True)
    budget_per_day = models.CharField(max_length=50, blank=True)
    language_tip = models.CharField(max_length=200, blank=True)
    safety_tips = models.TextField(blank=True)
    local_food = models.TextField(blank=True)
    how_to_reach = models.TextField(blank=True)
    cover_image_url = models.URLField(blank=True)
    crowd_level = models.CharField(max_length=20, default='moderate')
    safety_rating = models.PositiveSmallIntegerField(default=4)
    budget_tier = models.CharField(max_length=4, default='$$')
    best_season_json = models.TextField(
        default='{}',
        help_text='JSON: {"Jan":"green","Feb":"yellow",...}'
    )
    best_time_to_visit = models.CharField(max_length=100, blank=True)
    getting_there = models.TextField(blank=True)
    local_transport = models.TextField(blank=True)
    must_visit_spots = models.TextField(blank=True)
    estimated_budget_per_day = models.CharField(max_length=60, blank=True)
    language_tips = models.TextField(blank=True)
    emergency_numbers = models.TextField(blank=True)
    tourist_office_contact = models.CharField(max_length=200, blank=True)

    def __str__(self):
        return self.name


class Itinerary(models.Model):
    """User's day-by-day trip plan — built in the bucket list page."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='itineraries')
    title = models.CharField(max_length=200)
    destination_name = models.CharField(max_length=200)
    start_date = models.DateField(null=True, blank=True)
    days_count = models.PositiveSmallIntegerField(default=3)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username}: {self.title}"


class ItineraryItem(models.Model):
    TIME_CHOICES = [('morning', 'Morning'), ('afternoon', 'Afternoon'), ('evening', 'Evening')]
    itinerary = models.ForeignKey(Itinerary, on_delete=models.CASCADE, related_name='items')
    day_number = models.PositiveSmallIntegerField(default=1)
    time_block = models.CharField(max_length=15, choices=TIME_CHOICES, default='morning')
    activity = models.CharField(max_length=300)
    notes = models.TextField(blank=True)
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ['day_number', 'order']


class Collection(models.Model):
    """Named collections a user saves posts into."""
    COLLECTION_TYPES = [
        ('bucket_list', 'Bucket List'),
        ('dream_trips', 'Dream Trips'),
        ('visited', 'Visited'),
        ('favorites', 'Favorites'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='collections')
    name = models.CharField(max_length=30, choices=COLLECTION_TYPES, default='favorites')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'name')

    def __str__(self):
        return f"{self.user.username} → {self.name}"


class CollectionItem(models.Model):
    collection = models.ForeignKey(Collection, on_delete=models.CASCADE, related_name='items')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='in_collections')
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('collection', 'post')


class Reaction(models.Model):
    """Emoji reactions on posts (love / wow / haha / sad / fire)."""
    REACTION_TYPES = [
        ('love', '❤️ Love'),
        ('wow', '🤩 Wow'),
        ('haha', '😂 Haha'),
        ('sad', '😢 Sad'),
        ('fire', '🔥 Fire'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reactions')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='reactions')
    reaction_type = models.CharField(max_length=10, choices=REACTION_TYPES)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'post')

    def __str__(self):
        return f"{self.user.username} {self.reaction_type} on post {self.post_id}"


# ── COMMUNITY MODELS ────────────────────────────────────────────


class ChatRoom(models.Model):
    """Community chat rooms: global, destination-based, country-based, etc."""
    ROOM_TYPES = [
        ('global', 'Global Chat'),
        ('destination', 'Destination Chat'),
        ('country', 'Country Chat'),
        ('solo', 'Solo Traveler Chat'),
        ('backpacker', 'Backpacker Chat'),
        ('custom', 'Custom Chat'),
    ]
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True)
    room_type = models.CharField(max_length=20, choices=ROOM_TYPES, default='global')
    description = models.TextField(blank=True, max_length=500)
    icon = models.CharField(max_length=10, default='💬')
    members = models.ManyToManyField(User, related_name='chat_rooms', blank=True)
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-is_default', 'name']

    def __str__(self):
        return self.name

    @property
    def member_count(self):
        return self.members.count()

    @property
    def last_message(self):
        return self.messages.order_by('-created_at').first()


class ChatMessage(models.Model):
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name='messages')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chat_messages')
    text = models.TextField(max_length=2000)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"{self.user.username}: {self.text[:50]}"


class TravelGroup(models.Model):
    """Travel interest groups: beaches, mountains, food, etc."""
    CATEGORY_CHOICES = [
        ('beach', 'Beaches'),
        ('mountain', 'Mountains'),
        ('food', 'Food & Culinary'),
        ('nature', 'Nature & Wildlife'),
        ('island', 'Islands'),
        ('adventure', 'Adventure'),
        ('cultural', 'Cultural'),
        ('budget', 'Budget Travel'),
        ('luxury', 'Luxury Travel'),
        ('solo', 'Solo Travel'),
        ('photography', 'Travel Photography'),
    ]
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True)
    category = models.CharField(max_length=30, choices=CATEGORY_CHOICES)
    description = models.TextField(blank=True, max_length=800)
    icon = models.CharField(max_length=10, default='🌍')
    cover_url = models.URLField(blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_groups')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    @property
    def member_count(self):
        return self.memberships.count()


class GroupMembership(models.Model):
    ROLE_CHOICES = [
        ('member', 'Member'),
        ('moderator', 'Moderator'),
        ('admin', 'Admin'),
    ]
    group = models.ForeignKey(TravelGroup, on_delete=models.CASCADE, related_name='memberships')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='group_memberships')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='member')
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('group', 'user')

    def __str__(self):
        return f"{self.user.username} in {self.group.name}"


class CommunityEvent(models.Model):
    """Community events: meetups, group trips, travel challenges."""
    EVENT_TYPES = [
        ('meetup', 'Meetup'),
        ('group_trip', 'Group Trip'),
        ('challenge', 'Travel Challenge'),
        ('workshop', 'Workshop'),
        ('virtual', 'Virtual Hangout'),
    ]
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True)
    event_type = models.CharField(max_length=20, choices=EVENT_TYPES, default='meetup')
    description = models.TextField(blank=True, max_length=2000)
    location = models.CharField(max_length=200, blank=True)
    country = models.CharField(max_length=100, blank=True)
    start_date = models.DateTimeField(null=True, blank=True)
    end_date = models.DateTimeField(null=True, blank=True)
    max_attendees = models.PositiveIntegerField(default=50)
    cover_url = models.URLField(blank=True)
    organizer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='organized_events')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['start_date', '-created_at']

    def __str__(self):
        return self.title

    @property
    def attendee_count(self):
        return self.rsvps.filter(status='going').count()

    @property
    def spots_left(self):
        return max(0, self.max_attendees - self.attendee_count)


class EventRSVP(models.Model):
    STATUS_CHOICES = [
        ('going', 'Going'),
        ('interested', 'Interested'),
        ('not_going', 'Not Going'),
    ]
    event = models.ForeignKey(CommunityEvent, on_delete=models.CASCADE, related_name='rsvps')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='event_rsvps')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='interested')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('event', 'user')


class TripJoinRequest(models.Model):
    """Request to join a travel companion trip."""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('declined', 'Declined'),
    ]
    trip = models.ForeignKey(TravelCompanion, on_delete=models.CASCADE, related_name='join_requests')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='trip_requests')
    message = models.TextField(blank=True, max_length=500)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('trip', 'user')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} → {self.trip.destination} ({self.status})"


# ── BACKWARD-COMPAT RE-EXPORTS ───────────────────────────────────
def trending_posts(limit=5):
    from .services import trending_posts as _trending
    return _trending(limit)


def top_explorers(limit=5):
    from .services import top_explorers as _top
    return _top(limit)

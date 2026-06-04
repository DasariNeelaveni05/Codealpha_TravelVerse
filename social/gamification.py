"""
Explorer gamification: badges, XP, milestones, achievements, and hidden gem scoring.
"""

from django.db.models import Count

# (min_xp, slug, display_name, icon)
BADGE_TIERS = [
    (0, 'explorer', 'Explorer', '🧭'),
    (100, 'bronze', 'Bronze Explorer', '🥉'),
    (400, 'silver', 'Silver Backpacker', '🥈'),
    (1000, 'gold', 'Gold Nomad', '🥇'),
    (2000, 'platinum', 'Platinum Traveler', '💎'),
]

ACHIEVEMENT_DEFINITIONS = [
    ('first_post', 'First Steps', 'Published your first travel post', '📸', lambda u: u.posts.exists()),
    ('five_posts', 'Storyteller', 'Shared 5 travel posts', '🗺️', lambda u: u.posts.count() >= 5),
    ('first_gem', 'Gem Hunter', 'Marked a destination as a hidden gem', '💎', lambda u: u.posts.filter(is_hidden_gem=True).exists()),
    ('ten_likes', 'Crowd Favorite', 'Received 10 likes on your posts', '❤️', lambda u: _received_likes(u) >= 10),
    ('first_follower', 'Rising Explorer', 'Gained your first follower', '👥', lambda u: u.followers_set.exists()),
    ('passport_3', 'Globe Trotter', 'Visited 3 countries (passport stamps)', '🌍', lambda u: u.passport_stamps.values('country').distinct().count() >= 3),
    ('bucket_5', 'Dream Planner', 'Added 5 destinations to bucket list', '🪣', lambda u: u.bucket_list.count() >= 5),
    ('first_reel', 'Reel Creator', 'Uploaded your first travel reel', '🎬', lambda u: u.reels.exists()),
    ('first_blog', 'Travel Writer', 'Published your first travelogue', '📖', lambda u: u.blogs.exists()),
    ('platinum_path', 'Elite Path', 'Reached 1500+ explorer points', '🏆', lambda u: u.profile.explorer_score >= 1500),
]

# Demo map pins: country -> (x%, y%) on simplified world SVG
COUNTRY_MAP_PINS = {
    'Japan': (86, 38),
    'Italy': (52, 36),
    'Iceland': (44, 22),
    'Brazil': (32, 62),
    'Australia': (88, 72),
    'USA': (22, 38),
    'United States': (22, 38),
    'France': (48, 34),
    'India': (72, 48),
    'Thailand': (78, 52),
    'Greece': (54, 40),
    'Morocco': (46, 44),
    'Peru': (28, 58),
    'New Zealand': (92, 78),
    'South Africa': (54, 72),
    'Canada': (20, 28),
    'Spain': (46, 38),
    'Indonesia': (82, 58),
    'Mexico': (18, 48),
    'Egypt': (58, 46),
}

CONTINENT_BY_COUNTRY = {
    'Japan': 'Asia', 'Thailand': 'Asia', 'India': 'Asia', 'Indonesia': 'Asia',
    'Italy': 'Europe', 'France': 'Europe', 'Spain': 'Europe', 'Greece': 'Europe',
    'Iceland': 'Europe', 'Morocco': 'Africa', 'Egypt': 'Africa', 'South Africa': 'Africa',
    'USA': 'North America', 'United States': 'North America', 'Canada': 'North America',
    'Mexico': 'North America', 'Brazil': 'South America', 'Peru': 'South America',
    'Australia': 'Oceania', 'New Zealand': 'Oceania',
}


def _received_likes(user):
    from .models import Like
    return Like.objects.filter(post__author=user).count()


def badge_tier_for_score(score):
    current = BADGE_TIERS[0]
    for tier in BADGE_TIERS:
        if score >= tier[0]:
            current = tier
        else:
            break
    return current


def next_badge_tier(score):
    for tier in BADGE_TIERS:
        if score < tier[0]:
            return tier
    return None


def explorer_progress(score):
    """XP progress bar data toward next badge."""
    current = badge_tier_for_score(score)
    nxt = next_badge_tier(score)
    if not nxt:
        return {
            'current_label': current[2],
            'current_icon': current[3],
            'current_slug': current[1],
            'next_label': None,
            'progress_percent': 100,
            'xp_current': score,
            'xp_next': score,
            'xp_into_tier': score - current[0],
            'xp_needed': 0,
            'max_tier': True,
        }
    tier_floor = current[0]
    tier_ceil = nxt[0]
    span = tier_ceil - tier_floor
    into = score - tier_floor
    pct = int((into / span) * 100) if span else 0
    return {
        'current_label': current[2],
        'current_icon': current[3],
        'current_slug': current[1],
        'next_label': nxt[2],
        'next_icon': nxt[3],
        'progress_percent': min(100, max(0, pct)),
        'xp_current': score,
        'xp_next': tier_ceil,
        'xp_into_tier': into,
        'xp_needed': tier_ceil - score,
        'max_tier': False,
    }


def badge_display_name(short_name):
    """Map legacy short badge names to full titles."""
    mapping = {
        'Explorer': 'Explorer',
        'Bronze': 'Bronze Explorer',
        'Silver': 'Silver Backpacker',
        'Gold': 'Gold Nomad',
        'Platinum': 'Platinum Traveler',
    }
    return mapping.get(short_name, short_name)


def calculate_hidden_gem_score(post):
    """
    Hidden Gem Score (0–100) from engagement, saves, votes, and ratings.
    """
    from .models import SavedPost

    likes = post.likes.count()
    comments = post.comments.count()
    saves = SavedPost.objects.filter(post=post).count()
    votes = post.gem_votes
    rating_bonus = (post.safety_rating or 3) * 2
    base = likes * 4 + comments * 6 + saves * 10 + votes * 12 + rating_bonus
    if post.is_hidden_gem:
        base += 15
    if post.hidden_gem_description:
        base += 5
    return min(100, base)


def is_certified_hidden_gem(post):
    """Community-certified when votes and score thresholds are met."""
    score = post.hidden_gem_score if hasattr(post, 'hidden_gem_score') else calculate_hidden_gem_score(post)
    return post.is_hidden_gem and post.gem_votes >= 3 and score >= 35


def sync_user_achievements(user):
    """Persist unlocked achievements; return list of newly unlocked achievement dicts."""
    from .models import UserAchievement

    newly_unlocked = []
    for ach in get_achievements_for_user(user):
        if ach['unlocked']:
            _, created = UserAchievement.objects.get_or_create(user=user, key=ach['key'])
            if created:
                newly_unlocked.append(ach)
    return newly_unlocked


def get_achievements_for_user(user):
    """Return list of achievement dicts with unlocked status."""
    results = []
    for key, title, desc, icon, check_fn in ACHIEVEMENT_DEFINITIONS:
        try:
            unlocked = check_fn(user)
        except Exception:
            unlocked = False
        results.append({
            'key': key,
            'title': title,
            'description': desc,
            'icon': icon,
            'unlocked': unlocked,
        })
    return results


def get_travel_statistics(user):
    """Comprehensive travel & engagement stats for dashboards and profiles."""
    from .models import HiddenGemVote, Like, Post, SavedPost

    stamps = user.passport_stamps.all()
    countries = stamps.values('country').distinct().count()
    states = stamps.exclude(state='').values('state').distinct().count()
    cities = stamps.exclude(city='').values('city').distinct().count()
    continents = set()
    for c in stamps.values_list('country', flat=True):
        cont = CONTINENT_BY_COUNTRY.get(c) or ''
        if cont:
            continents.add(cont)
    for cont in stamps.exclude(continent='').values_list('continent', flat=True):
        if cont:
            continents.add(cont)
    continents_count = len(continents)

    posts_count = user.posts.count()
    gems_discovered = user.posts.filter(is_hidden_gem=True).count()
    from .models import Comment

    received_likes = Like.objects.filter(post__author=user).count()
    received_comments = Comment.objects.filter(post__author=user).count()
    followers = user.followers_set.count()
    following = user.following_set.count()
    total_engagement = received_likes + received_comments + HiddenGemVote.objects.filter(post__author=user).count()
    engagement_rate = round((total_engagement / max(posts_count, 1)) * 10, 1)

    profile = user.profile
    profile.recalculate_explorer_score()
    progress = explorer_progress(profile.explorer_score)
    achievements = get_achievements_for_user(user)
    unlocked_count = sum(1 for a in achievements if a['unlocked'])

    return {
        'posts': posts_count,
        'reels': user.reels.count(),
        'blogs': user.blogs.count(),
        'countries': countries,
        'states': states,
        'cities': cities,
        'continents': continents_count,
        'gems_discovered': gems_discovered,
        'bucket_list': user.bucket_list.count(),
        'saved_posts': SavedPost.objects.filter(user=user).count(),
        'followers': followers,
        'following': following,
        'explorer_score': profile.explorer_score,
        'badge': progress['current_label'],
        'badge_icon': progress['current_icon'],
        'badge_slug': progress['current_slug'],
        'progress': progress,
        'engagement_rate': min(engagement_rate, 100),
        'achievements_unlocked': unlocked_count,
        'achievements_total': len(ACHIEVEMENT_DEFINITIONS),
        'achievements': achievements,
    }


def map_pins_for_stamps(stamps):
    """Build visual map pin data from passport stamps."""
    pins = []
    seen = set()
    for stamp in stamps:
        country = stamp.country
        if country in seen:
            continue
        coords = COUNTRY_MAP_PINS.get(country)
        if coords:
            pins.append({
                'country': country,
                'x': coords[0],
                'y': coords[1],
                'city': stamp.city,
            })
            seen.add(country)
    return pins

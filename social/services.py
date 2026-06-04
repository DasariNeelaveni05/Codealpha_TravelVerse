"""Shared query helpers for feeds, sidebars, and search."""

from django.contrib.auth.models import User
from django.db.models import Count, Q

from .gamification import calculate_hidden_gem_score
from .models import Post, Profile


def update_post_gem_score(post):
    score = calculate_hidden_gem_score(post)
    if post.hidden_gem_score != score:
        Post.objects.filter(pk=post.pk).update(hidden_gem_score=score)
        post.hidden_gem_score = score
    return score


def trending_posts(limit=5):
    return (
        Post.objects.select_related('author', 'author__profile')
        .prefetch_related('images')
        .filter(is_hidden_gem=True)
        .order_by('-hidden_gem_score', '-gem_votes', '-created_at')[:limit]
    )


def top_explorers(limit=5):
    return Profile.objects.select_related('user').order_by('-explorer_score')[:limit]


def featured_destinations(limit=4):
    return (
        Post.objects.select_related('author')
        .prefetch_related('images')
        .filter(is_hidden_gem=True)
        .order_by('-hidden_gem_score')[:limit]
    )


def community_highlights(limit=5):
    return (
        Post.objects.annotate(
            engagement=Count('likes', distinct=True) + Count('comments', distinct=True),
        )
        .select_related('author', 'author__profile')
        .prefetch_related('images')
        .order_by('-engagement', '-created_at')[:limit]
    )


def recommended_trips(limit=4):
    """Featured demo trips for sidebar widget."""
    return [
        {'title': 'Kyoto Temple Trail', 'location': 'Japan', 'budget': '$800', 'icon': '⛩️'},
        {'title': 'Amalfi Coast Drive', 'location': 'Italy', 'budget': '$1,200', 'icon': '🌊'},
        {'title': 'Northern Lights Hunt', 'location': 'Iceland', 'budget': '$1,500', 'icon': '🌌'},
        {'title': 'Patagonia Trek', 'location': 'Argentina', 'budget': '$2,000', 'icon': '🏔️'},
    ][:limit]


def travel_challenges():
    """Weekly community challenges — mix of dynamic counts and demo copy."""
    from .models import Post

    gem_count = Post.objects.filter(is_hidden_gem=True).count()
    return [
        {'title': 'Hidden Gem Hunter', 'desc': f'Discover {max(gem_count, 12)}+ community gems', 'icon': '💎', 'progress': min(100, gem_count * 5)},
        {'title': '7-Day Explorer', 'desc': 'Post 3 destinations this week', 'icon': '🔥', 'progress': 40},
        {'title': 'Budget Backpacker', 'desc': 'Share a trip under $500', 'icon': '💰', 'progress': 65},
        {'title': 'Reel Wanderer', 'desc': 'Upload a vertical travel reel', 'icon': '🎬', 'progress': 20},
    ]


def sidebar_widgets(request):
    user = request.user
    base = {
        'trending': trending_posts(5),
        'top_explorers': top_explorers(5),
        'featured_destinations': featured_destinations(4),
        'community_highlights': community_highlights(4),
        'recommended_trips': recommended_trips(4),
        'travel_challenges': travel_challenges(),
        'suggested_users': [],
    }
    if user.is_authenticated:
        base['suggested_users'] = (
            User.objects.exclude(pk=user.pk)
            .annotate(follower_count=Count('followers_set'))
            .order_by('-follower_count')[:5]
        )
    else:
        base['suggested_users'] = User.objects.all()[:5]
    return base


def search_posts(q, category=None):
    qs = Post.objects.select_related('author', 'author__profile').prefetch_related('images')
    if q:
        qs = qs.filter(
            Q(location__icontains=q)
            | Q(city__icontains=q)
            | Q(country__icontains=q)
            | Q(caption__icontains=q)
            | Q(hidden_gem_description__icontains=q)
        )
    if category:
        qs = qs.filter(category=category)
    return qs.distinct().order_by('-hidden_gem_score', '-created_at')[:24]

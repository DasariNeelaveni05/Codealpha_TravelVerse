import json
from datetime import date
from decimal import Decimal

from django.contrib import messages
from django.contrib.auth import login, logout
from django.db import transaction
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.db.models import Count, Exists, OuterRef, Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.text import slugify
from django.views.decorators.http import require_POST

from .forms import (
    BlogForm,
    BucketListForm,
    CommentForm,
    PostForm,
    ProfileEditForm,
    ReelForm,
    SignUpForm,
    TravelCompanionForm,
)
from .gamification import CONTINENT_BY_COUNTRY, get_travel_statistics, map_pins_for_stamps, sync_user_achievements
from .map_data import COUNTRY_COORDS, map_markers_from_posts
from .models import (
    Blog,
    BucketList,
    ChatMessage,
    ChatRoom,
    Comment,
    CommunityEvent,
    DirectMessage,
    EventRSVP,
    Follow,
    GroupMembership,
    GuideProfile,
    TouristHelpRequest,
    HiddenGemVote,
    Like,
    Notification,
    PassportStamp,
    Post,
    PostImage,
    Profile,
    Reel,
    ReelLike,
    SavedPost,
    TravelCompanion,
    TravelGroup,
    TripJoinRequest,
)
from .placeholders import DEMO_DESTINATIONS
from .services import sidebar_widgets, update_post_gem_score
from .utils import validate_image_upload

POST_CATEGORIES = [
    ('beach', 'Beaches'),
    ('mountain', 'Mountains'),
    ('adventure', 'Adventure'),
    ('historical', 'Historical Places'),
    ('food', 'Food Destinations'),
    ('nature', 'Nature'),
    ('island', 'Islands'),
    ('budget', 'Budget Travel'),
]


def _json_error(message, status=400):
    return JsonResponse({'ok': False, 'error': message}, status=status)


def _notify(recipient, actor, ntype, message, post=None, reel=None):
    if recipient == actor:
        return
    Notification.objects.create(
        recipient=recipient,
        actor=actor,
        notification_type=ntype,
        message=message,
        post=post,
        reel=reel,
    )


def _sidebar_context(request):
    return sidebar_widgets(request)


def _feed_posts(user, page=1, per_page=6, category=None):
    """Show all public posts from all users for a continuous global feed."""
    qs = Post.objects.all()
    valid_categories = {choice[0] for choice in Post.CATEGORY_CHOICES}
    
    if category in valid_categories:
        qs = qs.filter(category=category)
        
    qs = qs.select_related('author', 'author__profile').prefetch_related('images', 'likes')
    if user.is_authenticated:
        qs = qs.annotate(
            user_liked=Exists(Like.objects.filter(user=user, post_id=OuterRef('pk'))),
            user_saved=Exists(SavedPost.objects.filter(user=user, post_id=OuterRef('pk'))),
            author_is_followed=Exists(
                Follow.objects.filter(follower=user, following_id=OuterRef('author_id'))
            ),
        )
    paginator = Paginator(qs, per_page)
    return paginator.get_page(page)


def _stamp_from_post(user, post):
    if not post.country:
        return
    continent = CONTINENT_BY_COUNTRY.get(post.country, '')
    PassportStamp.objects.get_or_create(
        user=user,
        country=post.country,
        city=post.city or '',
        defaults={
            'state': post.state,
            'continent': continent,
            'visited_at': date.today(),
            'post': post,
            'stamp_label': post.location[:120],
        },
    )


def _geocode_post(post):
    if post.country and post.country in COUNTRY_COORDS:
        lat, lng = COUNTRY_COORDS[post.country]
        post.latitude = Decimal(str(lat))
        post.longitude = Decimal(str(lng))
        post.save(update_fields=['latitude', 'longitude'])


def home_view(request):
    from .models import Post, UserProfile
    from django.db.models import F
    
    trending_posts = Post.objects.annotate(gem_score=F('hidden_gem_score')).order_by(
        '-gem_score', '-created_at'
    ).select_related('author', 'author__profile')[:6]
    
    top_explorers = UserProfile.objects.order_by(
        '-explorer_score'
    ).select_related('user')[:6]
    
    # Placeholder destinations if no posts yet
    placeholder_destinations = [
        {'name':'Santorini, Greece',  'img':'https://images.unsplash.com/photo-1570077188670-e3a8d69ac5ff?w=600&q=80', 'score':9.4, 'meta':'❤️ 2.8K · Island'},
        {'name':'Spiti Valley, India','img':'https://images.unsplash.com/photo-1464822759023-fed622ff2c3b?w=600&q=80', 'score':9.1, 'meta':'❤️ 1.5K · Mountain'},
        {'name':'Maldives Atoll',     'img':'https://images.unsplash.com/photo-1514282401047-d79a71a590e8?w=600&q=80', 'score':9.6, 'meta':'❤️ 5.2K · Beach'},
        {'name':'Kyoto, Japan',       'img':'https://images.unsplash.com/photo-1493976040374-85c8e12f0c0e?w=600&q=80', 'score':9.3, 'meta':'❤️ 4.1K · Historical'},
        {'name':'Faroe Islands',      'img':'https://images.unsplash.com/photo-1520769945061-0a448c463865?w=600&q=80', 'score':9.8, 'meta':'❤️ 3.4K · Nature'},
        {'name':'Kerala, India',      'img':'https://images.unsplash.com/photo-1501854140801-50d01698950b?w=600&q=80', 'score':8.8, 'meta':'❤️ 2.1K · Nature'},
    ]
    
    return render(request, 'landing.html', {
        'trending_posts': trending_posts,
        'top_explorers': top_explorers,
        'placeholder_destinations': placeholder_destinations,
        'show_footer': False,
    })


def landing(request):
    if request.user.is_authenticated:
        return redirect('feed')
    return home_view(request)


@login_required
def feed(request):
    page = request.GET.get('page', 1)
    category = request.GET.get('category')
    posts = _feed_posts(request.user, page, category=category)
    map_markers = map_markers_from_posts(
        Post.objects.filter(is_hidden_gem=True).select_related('author')[:50]
    )

    # Instagram-style Stories: prioritizing followed users
    stories = Profile.objects.filter(
        user__followers_set__follower=request.user
    ).select_related('user').distinct()
    
    # Fallback to active explorers if user follows no one
    if not stories.exists():
        stories = Profile.objects.select_related('user').filter(
            user__posts__isnull=False
        ).distinct().order_by('-explorer_score')[:15]

    ctx = {
        'posts': posts,
        # Removed feed_reels to keep Feed exclusive to posts and stories
        'stories': stories,
        'map_markers_json': json.dumps(map_markers),
        'demo_destinations': DEMO_DESTINATIONS,
        **_sidebar_context(request),
    }
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        html = render(request, 'partials/feed_items.html', ctx).content.decode()
        return JsonResponse({
            'ok': True,
            'html': html,
            'has_next': posts.has_next(),
            'next_page': posts.next_page_number() if posts.has_next() else None,
        })
    return render(request, 'feed.html', ctx)


def register_view(request):
    if request.user.is_authenticated:
        return redirect('feed')
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            user.profile.recalculate_explorer_score()
            sync_user_achievements(user)
            messages.success(request, 'Welcome to TravelVerse! Start exploring hidden gems.')
            return redirect('feed')
        messages.error(request, 'Please fix the errors below to create your account.')
    else:
        form = SignUpForm()
    return render(request, 'register.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('feed')
    return render(request, 'login.html')


@login_required
def logout_view(request):
    logout(request)
    messages.info(request, 'You have been logged out. Safe travels!')
    return redirect('landing')


@login_required
def profile_view(request, username):
    profile_user = get_object_or_404(User, username=username)
    posts = profile_user.posts.select_related('author').prefetch_related('images')[:12]
    reels = profile_user.reels.all()[:8]
    blogs = profile_user.blogs.all()[:6]
    is_following = False
    if request.user != profile_user:
        is_following = Follow.objects.filter(follower=request.user, following=profile_user).exists()
    travel_stats = get_travel_statistics(profile_user)
    sync_user_achievements(profile_user)
    stamps = profile_user.passport_stamps.all()
    timeline = stamps.select_related('post')[:15]
    ctx = {
        'profile_user': profile_user,
        'posts': posts,
        'reels': reels,
        'blogs': blogs,
        'is_following': is_following,
        'stats': travel_stats,
        'travel_stats': travel_stats,
        'stamps': stamps[:20],
        'timeline': timeline,
        'passport_summary': {
            'countries': travel_stats['countries'],
            'cities': travel_stats['cities'],
            'continents': travel_stats['continents'],
        },
    }
    ctx.update(_sidebar_context(request))
    return render(request, 'profile.html', ctx)


@login_required
def followers_list(request, username):
    profile_user = get_object_or_404(User, username=username)
    followers = User.objects.filter(following_set__following=profile_user).select_related('profile')
    return render(request, 'followers.html', {
        'profile_user': profile_user,
        'users': followers,
        **_sidebar_context(request),
    })


@login_required
def following_list(request, username):
    profile_user = get_object_or_404(User, username=username)
    following = User.objects.filter(followers_set__follower=profile_user).select_related('profile')
    return render(request, 'following.html', {
        'profile_user': profile_user,
        'users': following,
        **_sidebar_context(request),
    })


@login_required
def profile_edit(request):
    profile = request.user.profile
    if request.method == 'POST':
        form = ProfileEditForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully.')
            return redirect('profile', username=request.user.username)
    else:
        form = ProfileEditForm(instance=profile)
    return render(request, 'profile_edit.html', {'form': form, **_sidebar_context(request)})


@login_required
def create_post(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            with transaction.atomic():
                post = form.save(commit=False)
                post.author = request.user
                post.save()
                images = request.FILES.getlist('images')
                video = request.FILES.get('video')
                if not images and not video:
                    messages.error(request, 'Please upload at least one image or a video.')
                    return render(request, 'create_post.html', {'form': form, **_sidebar_context(request)})
                for idx, img in enumerate(images):
                    validate_image_upload(img)
                    PostImage.objects.create(post=post, image=img, order=idx)
                if video and not images:
                    messages.info(request, 'Video noted — upload a dedicated Reel for best playback.')
                _stamp_from_post(request.user, post)
                _geocode_post(post)
                update_post_gem_score(post)
                request.user.profile.recalculate_explorer_score()
                sync_user_achievements(request.user)
            messages.success(request, 'Your travel post is live!')
            return redirect('feed')
        messages.error(request, 'Please correct the errors below.')
    else:
        form = PostForm()
    return render(request, 'create_post.html', {'form': form, **_sidebar_context(request)})


@login_required
def create_reel(request):
    if request.method == 'POST':
        form = ReelForm(request.POST, request.FILES)
        if form.is_valid():
            reel = form.save(commit=False)
            reel.author = request.user
            reel.save()
            request.user.profile.recalculate_explorer_score()
            sync_user_achievements(request.user)
            messages.success(request, 'Reel uploaded!')
            return redirect('reels')
    else:
        form = ReelForm()
    return render(request, 'create_reel.html', {'form': form, **_sidebar_context(request)})


@login_required
def create_blog(request):
    if request.method == 'POST':
        form = BlogForm(request.POST, request.FILES)
        if form.is_valid():
            blog = form.save(commit=False)
            blog.author = request.user
            base_slug = slugify(blog.title) or 'travelogue'
            slug = base_slug
            n = 1
            while Blog.objects.filter(slug=slug).exists():
                slug = f'{base_slug}-{n}'
                n += 1
            blog.slug = slug
            blog.save()
            request.user.profile.recalculate_explorer_score()
            sync_user_achievements(request.user)
            messages.success(request, 'Travelogue published!')
            return redirect('blog_detail', slug=blog.slug)
    else:
        form = BlogForm()
    return render(request, 'create_blog.html', {'form': form, **_sidebar_context(request)})


@login_required
def blog_list(request):
    blogs = Blog.objects.select_related('author', 'author__profile').all()
    return render(request, 'blog_list.html', {'blogs': blogs, **_sidebar_context(request)})


def blog_detail(request, slug):
    blog = get_object_or_404(Blog.objects.select_related('author', 'author__profile'), slug=slug)
    comments = blog.comments.filter(parent__isnull=True).select_related('user', 'user__profile')
    ctx = {'blog': blog, 'comments': comments}
    if request.user.is_authenticated:
        ctx.update(_sidebar_context(request))
    return render(request, 'blog_detail.html', ctx)


@login_required
def reels_view(request):
    reels = Reel.objects.select_related(
        'author', 'author__profile'
    ).order_by('-created_at')

    liked_reels = set(
        ReelLike.objects.filter(user=request.user).values_list('reel_id', flat=True)
    )

    # Attach guide reel ids (reels whose author has a guide profile)
    guide_author_ids = set(
        GuideProfile.objects.values_list('user_id', flat=True)
    )
    guide_reel_ids = set(
        r.id for r in reels if r.author_id in guide_author_ids
    )

    return render(request, 'reels.html', {
        'reels': reels,
        'liked_reels': liked_reels,
        'guide_reel_ids': guide_reel_ids,
        'show_footer': False,
        'active_page': 'reels',
    })



@login_required
def explore(request):
    gems = list(
        Post.objects.filter(is_hidden_gem=True)
        .select_related('author', 'author__profile')
        .prefetch_related('images')
        .annotate(vote_count=Count('votes'))
        .order_by('-hidden_gem_score', '-gem_votes', '-vote_count')[:24]
    )
    map_markers = map_markers_from_posts(gems) or [
        {
            'lat': d['lat'], 'lng': d['lng'], 'title': d['name'],
            'url': '#', 'score': 0, 'category': d['category'],
        }
        for d in DEMO_DESTINATIONS
    ]
    return render(request, 'explore.html', {
        'gems': gems,
        'map_markers_json': json.dumps(map_markers),
        **_sidebar_context(request),
    })


@login_required
def search_view(request):
    q = request.GET.get('q', '').strip()
    category = request.GET.get('category', '').strip()
    users = (
        User.objects.filter(Q(username__icontains=q) | Q(profile__bio__icontains=q))
        .select_related('profile')[:12]
        if q else []
    )
    from .services import search_posts
    locations = search_posts(q, category or None) if q or category else []
    return render(request, 'search.html', {
        'q': q,
        'category': category,
        'users': users,
        'locations': locations,
        'categories': POST_CATEGORIES,
        **_sidebar_context(request),
    })


@login_required
def bucket_list_view(request):
    saved = SavedPost.objects.filter(
        user=request.user
    ).select_related('post','post__author').order_by('-saved_at')
    return render(request, 'bucket_list.html', {
        'saved_items': saved,
        'show_footer': False,
        'active_page': 'bucketlist',
    })


@login_required
def notifications_view(request):
    if request.GET.get('mark_read'):
        Notification.objects.filter(
            recipient=request.user, is_read=False
        ).update(is_read=True)
    notifs = Notification.objects.filter(
        recipient=request.user
    ).select_related('actor','post').order_by('-created_at')[:50]
    return render(request, 'notifications.html', {
        'notifications': notifs,
        'show_footer': False,
        'active_page': 'notifications',
    })


@login_required
def passport_view(request):
    stamps = request.user.passport_stamps.all()
    by_country = {}
    for s in stamps:
        by_country.setdefault(s.country, []).append(s)
    travel_stats = get_travel_statistics(request.user)
    map_pins = map_pins_for_stamps(stamps)
    if not map_pins:
        from .gamification import COUNTRY_MAP_PINS
        map_pins = [
            {'country': c, 'x': coords[0], 'y': coords[1], 'city': '', 'demo': True}
            for c, coords in list(COUNTRY_MAP_PINS.items())[:8]
        ]
        
    user_post_locations = []
    user_posts = Post.objects.filter(author=request.user, latitude__isnull=False, longitude__isnull=False)
    for p in user_posts:
        user_post_locations.append({
            'lat': float(p.latitude),
            'lng': float(p.longitude),
            'location': p.location,
            'image_url': p.get_image()
        })
    if not user_post_locations:
        user_post_locations = [
            {'lat': 11.4102, 'lng': 76.6950, 'location': 'Ooty, India', 'image_url': 'https://images.unsplash.com/photo-1470770903676-69b98201ea1c?w=800'},
            {'lat': 32.2396, 'lng': 77.1887, 'location': 'Manali, India', 'image_url': 'https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=800'},
            {'lat': 15.3350, 'lng': 76.4600, 'location': 'Hampi, India', 'image_url': 'https://images.unsplash.com/photo-1590123715937-d26beb66a374?w=800'}
        ]

    return render(request, 'passport.html', {
        'stamps': stamps,
        'by_country': by_country,
        'travel_stats': travel_stats,
        'map_pins': map_pins,
        'user_post_locations_json': json.dumps(user_post_locations),
        'timeline': stamps[:20],
        **_sidebar_context(request),
    })


@login_required
def stats_dashboard(request):
    new_achievements = sync_user_achievements(request.user)
    travel_stats = get_travel_statistics(request.user)
    return render(request, 'stats_dashboard.html', {
        'travel_stats': travel_stats,
        'profile_user': request.user,
        'new_achievements': new_achievements,
        **_sidebar_context(request),
    })


@login_required
def saved_posts_view(request):
    saved = request.user.saved_posts.select_related('post', 'post__author', 'post__author__profile').all()
    return render(request, 'saved.html', {'saved': saved, **_sidebar_context(request)})


@login_required
@require_POST
def toggle_like(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    like, created = Like.objects.get_or_create(user=request.user, post=post)
    if not created:
        like.delete()
        liked = False
    else:
        liked = True
        _notify(post.author, request.user, 'like', f'{request.user.username} liked your post', post)
        post.author.profile.recalculate_explorer_score()
    update_post_gem_score(post)
    return JsonResponse({
        'ok': True,
        'liked': liked,
        'count': post.like_count,
        'gem_score': post.hidden_gem_score,
    })


@login_required
@require_POST
def toggle_reel_like(request, reel_id):
    reel = get_object_or_404(Reel, pk=reel_id)
    like, created = ReelLike.objects.get_or_create(user=request.user, reel=reel)
    if not created:
        like.delete()
        liked = False
    else:
        liked = True
        _notify(reel.author, request.user, 'like', f'{request.user.username} liked your reel', reel=reel)
        reel.author.profile.recalculate_explorer_score()

    return JsonResponse({
        'ok': True,
        'liked': liked,
        'count': reel.like_count,
    })


@login_required
@require_POST
def add_comment(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    data = json.loads(request.body) if request.content_type == 'application/json' else request.POST
    text = (data.get('text') or '').strip()
    parent_id = data.get('parent_id')
    if not text:
        return _json_error('Comment cannot be empty.')
    parent = None
    if parent_id:
        parent = get_object_or_404(Comment, pk=parent_id, post=post)
    comment = Comment.objects.create(user=request.user, post=post, text=text, parent=parent)
    ntype = 'reply' if parent else 'comment'
    msg = (
        f'{request.user.username} replied to your comment'
        if parent else f'{request.user.username} commented on your post'
    )
    _notify(post.author, request.user, ntype, msg, post)
    if parent:
        _notify(parent.user, request.user, 'reply', f'{request.user.username} replied to your comment', post)
    update_post_gem_score(post)
    post.author.profile.recalculate_explorer_score()
    return JsonResponse({
        'ok': True,
        'comment': {
            'id': comment.id,
            'text': comment.text,
            'user': request.user.username,
            'created': comment.created_at.strftime('%b %d'),
        },
        'count': post.comment_count,
        'gem_score': post.hidden_gem_score,
    })


@login_required
@require_POST
def toggle_follow(request, username):
    target = get_object_or_404(User, username=username)
    if target == request.user:
        return _json_error('You cannot follow yourself.')
    follow, created = Follow.objects.get_or_create(follower=request.user, following=target)
    if not created:
        follow.delete()
        following = False
    else:
        following = True
        _notify(target, request.user, 'follow', f'{request.user.username} started following you')
        target.profile.recalculate_explorer_score()
    return JsonResponse({
        'ok': True,
        'following': following,
        'followers_count': target.profile.followers_count,
    })


@login_required
@require_POST
def toggle_bucket(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    dest = post.location or post.city or f'Post #{post.id}'
    item = BucketList.objects.filter(user=request.user, destination_name=dest).first()
    if item:
        item.delete()
        saved = False
    else:
        BucketList.objects.create(user=request.user, post=post, destination_name=dest)
        saved = True
    return JsonResponse({'ok': True, 'saved': saved})


@login_required
@require_POST
def toggle_save_post(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    saved_obj, created = SavedPost.objects.get_or_create(user=request.user, post=post)
    if not created:
        saved_obj.delete()
        saved = False
    else:
        saved = True
    update_post_gem_score(post)
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.content_type == 'application/json':
        return JsonResponse({'ok': True, 'saved': saved, 'gem_score': post.hidden_gem_score})
    return redirect(request.META.get('HTTP_REFERER', 'bucket_list'))


@login_required
@require_POST
def vote_hidden_gem(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    vote, created = HiddenGemVote.objects.get_or_create(user=request.user, post=post)
    if not created:
        vote.delete()
        post.gem_votes = max(0, post.gem_votes - 1)
        voted = False
    else:
        post.gem_votes += 1
        voted = True
        _notify(post.author, request.user, 'gem_vote', f'{request.user.username} voted for your hidden gem', post)
    post.save(update_fields=['gem_votes'])
    update_post_gem_score(post)
    return JsonResponse({
        'ok': True,
        'voted': voted,
        'votes': post.gem_votes,
        'gem_score': post.hidden_gem_score,
        'certified': post.is_certified_gem,
    })


@login_required
def post_detail(request, pk):
    post = get_object_or_404(
        Post.objects.select_related('author', 'author__profile').prefetch_related('images', 'comments__user'),
        pk=pk,
    )
    comments = (
        post.comments.filter(parent__isnull=True)
        .select_related('user', 'user__profile')
        .prefetch_related('replies__user')
    )
    post.user_liked = Like.objects.filter(user=request.user, post=post).exists()
    post.user_saved = SavedPost.objects.filter(user=request.user, post=post).exists()
    post.author_is_followed = Follow.objects.filter(follower=request.user, following=post.author).exists()
    update_post_gem_score(post)
    
    # First-timer guide banner logic
    city_name = post.city or post.location
    user_has_posts_here = False
    if request.user.is_authenticated:
        user_has_posts_here = Post.objects.filter(author=request.user).filter(
            Q(city__iexact=city_name) | Q(location__icontains=city_name)
        ).exists()
    show_guide_banner = not user_has_posts_here

    # Destination info widget
    destination_info = Destination.objects.filter(
        Q(name__iexact=city_name) | Q(city__iexact=city_name)
    ).first()

    ctx = {
        'post': post,
        'comments': comments,
        'show_guide_banner': show_guide_banner,
        'destination_info': destination_info,
    }
    ctx.update(_sidebar_context(request))
    return render(request, 'post_detail.html', ctx)


@login_required
def companions_view(request):
    destination = request.GET.get('destination', '').strip()
    date_from = request.GET.get('from', '')
    trips = TravelCompanion.objects.filter(is_active=True).select_related('user', 'user__profile')
    if destination:
        trips = trips.filter(
            Q(destination__icontains=destination) | Q(country__icontains=destination)
        )
    if date_from:
        from django.utils.dateparse import parse_date

        parsed = parse_date(date_from)
        if parsed:
            trips = trips.filter(start_date__gte=parsed)
    form = TravelCompanionForm()
    if request.method == 'POST':
        form = TravelCompanionForm(request.POST)
        if form.is_valid():
            trip = form.save(commit=False)
            trip.user = request.user
            trip.save()
            messages.success(request, 'Your travel companion listing is live!')
            return redirect('companions')
    return render(request, 'companions.html', {
        'trips': trips[:40],
        'form': form,
        'filter_destination': destination,
        **_sidebar_context(request),
    })


# ── COMMUNITY HUB ───────────────────────────────────────────────


@login_required
def community_hub(request):
    """Main community networking page."""
    buddy_trips = TravelCompanion.objects.filter(is_active=True).select_related(
        'user', 'user__profile'
    )[:12]
    chat_rooms = ChatRoom.objects.all()[:10]
    groups = TravelGroup.objects.annotate(
        members_count=Count('memberships')
    ).order_by('-members_count')[:12]
    events = CommunityEvent.objects.filter(is_active=True).select_related('organizer')[:8]
    guides = GuideProfile.objects.filter(
        is_verified=True, availability_status=True
    ).select_related('user', 'user__profile')[:8]
    map_markers = map_markers_from_posts(
        Post.objects.filter(is_hidden_gem=True).select_related('author')[:50]
    )
    help_requests = TouristHelpRequest.objects.filter(is_resolved=False)[:10]
    user_groups = TravelGroup.objects.filter(
        memberships__user=request.user
    ) if request.user.is_authenticated else TravelGroup.objects.none()

    return render(request, 'community.html', {
        'buddy_trips': buddy_trips,
        'chat_rooms': chat_rooms,
        'groups': groups,
        'events': events,
        'guides': guides,
        'help_requests': help_requests,
        'user_groups': user_groups,
        'map_markers_json': json.dumps(map_markers),
        **_sidebar_context(request),
    })


@login_required
def community_view(request):
    from .models import UserProfile
    buddy_trips = TravelCompanion.objects.filter(is_active=True).select_related('user', 'user__profile')
    chat_rooms = ChatRoom.objects.all()
    groups = TravelGroup.objects.all()
    events = CommunityEvent.objects.filter(is_active=True).select_related('organizer')
    guides = GuideProfile.objects.filter(is_verified=True).select_related('user', 'user__profile')
    top = UserProfile.objects.select_related('user').order_by('-explorer_score')[:12]
    
    user_groups = TravelGroup.objects.none()
    if request.user.is_authenticated:
        user_groups = TravelGroup.objects.filter(memberships__user=request.user)

    return render(request, 'community.html', {
        'buddy_trips': buddy_trips,
        'chat_rooms': chat_rooms,
        'groups': groups,
        'events': events,
        'guides': guides,
        'top_explorers': top,
        'user_groups': user_groups,
        'show_footer': False,
        'active_page': 'community',
        **_sidebar_context(request),
    })


@login_required
def guides_view(request):
    guides = GuideProfile.objects.filter(is_verified=True).select_related('user', 'user__profile')
    return render(request, 'guides.html', {
        'guides': guides,
        'show_footer': False,
        'active_page': 'guides',
        **_sidebar_context(request),
    })


@login_required
def chat_room_view(request, slug):
    room = get_object_or_404(ChatRoom, slug=slug)
    if request.user not in room.members.all():
        room.members.add(request.user)
    room_messages = room.messages.select_related('user', 'user__profile').order_by('-created_at')[:100]
    room_messages = list(reversed(room_messages))
    return render(request, 'chat_room.html', {
        'room': room,
        'messages_list': room_messages,
        **_sidebar_context(request),
    })


@login_required
@require_POST
def send_chat_message(request, slug):
    room = get_object_or_404(ChatRoom, slug=slug)
    data = json.loads(request.body) if request.content_type == 'application/json' else request.POST
    text = (data.get('text') or '').strip()
    if not text:
        return _json_error('Message cannot be empty.')
    msg = ChatMessage.objects.create(room=room, user=request.user, text=text)
    return JsonResponse({
        'ok': True,
        'message': {
            'id': msg.id,
            'text': msg.text,
            'user': request.user.username,
            'avatar': request.user.profile.get_avatar(),
            'created': msg.created_at.strftime('%I:%M %p'),
        },
    })


@login_required
def group_detail(request, slug):
    group = get_object_or_404(TravelGroup, slug=slug)
    is_member = GroupMembership.objects.filter(group=group, user=request.user).exists()
    members = group.memberships.select_related('user', 'user__profile')[:20]
    posts = Post.objects.filter(category=group.category).select_related(
        'author', 'author__profile'
    ).prefetch_related('images')[:12]
    return render(request, 'group_detail.html', {
        'group': group,
        'is_member': is_member,
        'members': members,
        'posts': posts,
        **_sidebar_context(request),
    })


@login_required
@require_POST
def toggle_group_membership(request, slug):
    group = get_object_or_404(TravelGroup, slug=slug)
    membership = GroupMembership.objects.filter(group=group, user=request.user).first()
    if membership:
        membership.delete()
        joined = False
    else:
        GroupMembership.objects.create(group=group, user=request.user)
        joined = True
    return JsonResponse({'ok': True, 'joined': joined, 'count': group.member_count})


@login_required
def event_detail(request, slug):
    event = get_object_or_404(CommunityEvent, slug=slug)
    user_rsvp = EventRSVP.objects.filter(event=event, user=request.user).first()
    attendees = event.rsvps.filter(status='going').select_related('user', 'user__profile')[:20]
    return render(request, 'event_detail.html', {
        'event': event,
        'user_rsvp': user_rsvp,
        'attendees': attendees,
        **_sidebar_context(request),
    })


@login_required
@require_POST
def toggle_event_rsvp(request, slug):
    event = get_object_or_404(CommunityEvent, slug=slug)
    data = json.loads(request.body) if request.content_type == 'application/json' else request.POST
    status = data.get('status', 'going')
    rsvp, created = EventRSVP.objects.get_or_create(
        event=event, user=request.user, defaults={'status': status}
    )
    if not created:
        if rsvp.status == status:
            rsvp.delete()
            return JsonResponse({'ok': True, 'rsvped': False, 'count': event.attendee_count})
        rsvp.status = status
        rsvp.save(update_fields=['status'])
    return JsonResponse({'ok': True, 'rsvped': True, 'status': status, 'count': event.attendee_count})


@login_required
@require_POST
def request_join_trip(request, trip_id):
    trip = get_object_or_404(TravelCompanion, pk=trip_id, is_active=True)
    if trip.user == request.user:
        return _json_error('You cannot join your own trip.')
    data = json.loads(request.body) if request.content_type == 'application/json' else request.POST
    message_text = (data.get('message') or '').strip()
    join_req, created = TripJoinRequest.objects.get_or_create(
        trip=trip, user=request.user, defaults={'message': message_text}
    )
    if not created:
        return _json_error('You have already requested to join this trip.')
    _notify(trip.user, request.user, 'follow', f'{request.user.username} wants to join your trip to {trip.destination}')
    return JsonResponse({'ok': True, 'requested': True})

import json
from datetime import date
from decimal import Decimal

from django.contrib import messages
from django.contrib.auth import login, logout
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
    EventRSVP,
    Follow,
    GroupMembership,
    GuideProfile,
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


def _notify(recipient, actor, ntype, message, post=None):
    if recipient == actor:
        return
    Notification.objects.create(
        recipient=recipient,
        actor=actor,
        notification_type=ntype,
        message=message,
        post=post,
    )


def _sidebar_context(request):
    return sidebar_widgets(request)


def _feed_posts(user, page=1, per_page=6, category=None):
    if user.is_authenticated:
        following_ids = user.following_set.values_list('following_id', flat=True)
        qs = Post.objects.filter(
            Q(author_id__in=following_ids) | Q(author=user) | Q(is_hidden_gem=True)
        ).distinct()
    else:
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


def landing(request):
    if request.user.is_authenticated:
        return redirect('feed')
    from .services import community_highlights, top_explorers, trending_posts
    return render(request, 'landing.html', {
        'trending': trending_posts(6),
        'top_explorers': top_explorers(6),
        'highlights': community_highlights(4),
    })


@login_required
def feed(request):
    page = request.GET.get('page', 1)
    category = request.GET.get('category')
    posts = _feed_posts(request.user, page, category=category)
    all_for_map = list(posts.object_list) if hasattr(posts, 'object_list') else list(posts)
    map_markers = map_markers_from_posts(
        Post.objects.filter(is_hidden_gem=True).select_related('author')[:30]
    )
    feed_reels = Reel.objects.select_related('author', 'author__profile').all()[:6]
    stories = Profile.objects.select_related('user').filter(
        user__posts__isnull=False
    ).distinct().order_by('-explorer_score')[:15]
    ctx = {
        'posts': posts,
        'feed_reels': feed_reels,
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
    reels = Reel.objects.select_related('author', 'author__profile').all()
    guide_cities = set()
    for guide in GuideProfile.objects.filter(availability_status=True):
        for city in guide.expertise_cities:
            guide_cities.add(city.strip().lower())

    guide_reel_ids = [
        reel.id
        for reel in reels
        if reel.location and any(city in reel.location.lower() for city in guide_cities)
    ]

    return render(request, 'reels.html', {
        'reels': reels,
        'guide_reel_ids': guide_reel_ids,
        **_sidebar_context(request),
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
    items = request.user.bucket_list.select_related('post').all()
    if request.method == 'POST':
        form = BucketListForm(request.POST)
        if form.is_valid():
            item = form.save(commit=False)
            item.user = request.user
            item.save()
            sync_user_achievements(request.user)
            messages.success(request, f'Added {item.destination_name} to your travel planner.')
            return redirect('bucket_list')
        messages.error(request, 'Could not add destination. Please check the form.')
    else:
        form = BucketListForm()
    travel_stats = get_travel_statistics(request.user)
    return render(request, 'bucket_list.html', {
        'items': items,
        'form': form,
        'travel_stats': travel_stats,
        **_sidebar_context(request),
    })


@login_required
def notifications_view(request):
    notifs = request.user.notifications.select_related('actor', 'post').all()[:50]
    request.user.notifications.filter(is_read=False).update(is_read=True)
    return render(request, 'notifications.html', {'notifications': notifs, **_sidebar_context(request)})


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
    return render(request, 'passport.html', {
        'stamps': stamps,
        'by_country': by_country,
        'travel_stats': travel_stats,
        'map_pins': map_pins,
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
    return JsonResponse({'ok': True, 'saved': saved, 'gem_score': post.hidden_gem_score})


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
    ctx = {'post': post, 'comments': comments}
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
    user_groups = TravelGroup.objects.filter(
        memberships__user=request.user
    ) if request.user.is_authenticated else TravelGroup.objects.none()

    return render(request, 'community.html', {
        'buddy_trips': buddy_trips,
        'chat_rooms': chat_rooms,
        'groups': groups,
        'events': events,
        'guides': guides,
        'user_groups': user_groups,
        'map_markers_json': json.dumps(map_markers),
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

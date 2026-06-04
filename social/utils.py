import re

from django.core.exceptions import ValidationError
from PIL import Image


ALLOWED_IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.webp', '.gif'}
MAX_IMAGE_SIZE_MB = 8
MAX_VIDEO_SIZE_MB = 50

EMOJI_PATTERN = re.compile(
    r'[\U0001F300-\U0001F9FF\U00002600-\U000027BF\U0001F600-\U0001F64F'
    r'\U0001F680-\U0001F6FF\U00002702-\U000027B0\U000024C2-\U0001F251]+',
    flags=re.UNICODE,
)

# ── Certified gem thresholds (single source of truth) ────────────
CERTIFIED_GEM_MIN_VOTES = 3
CERTIFIED_GEM_MIN_SCORE = 35


def validate_image_upload(image):
    if not image:
        return
    ext = '.' + image.name.rsplit('.', 1)[-1].lower()
    if ext not in ALLOWED_IMAGE_EXTENSIONS:
        raise ValidationError(
            f'Unsupported image type. Allowed: {", ".join(sorted(ALLOWED_IMAGE_EXTENSIONS))}'
        )
    if image.size > MAX_IMAGE_SIZE_MB * 1024 * 1024:
        raise ValidationError(f'Image must be under {MAX_IMAGE_SIZE_MB}MB.')
    try:
        img = Image.open(image)
        img.verify()
        image.seek(0)
    except Exception as exc:
        raise ValidationError('Invalid or corrupted image file.') from exc


def validate_video_upload(video):
    if not video:
        return
    allowed = {'.mp4', '.webm', '.mov'}
    ext = '.' + video.name.rsplit('.', 1)[-1].lower()
    if ext not in allowed:
        raise ValidationError(f'Unsupported video type. Allowed: {", ".join(sorted(allowed))}')
    if video.size > MAX_VIDEO_SIZE_MB * 1024 * 1024:
        raise ValidationError(f'Video must be under {MAX_VIDEO_SIZE_MB}MB.')


def validate_text_with_emojis(value, field_name='Field', max_length=2000, max_emojis=50):
    if not value:
        return value
    if len(value) > max_length:
        raise ValidationError(f'{field_name} must be at most {max_length} characters.')
    emojis = EMOJI_PATTERN.findall(value)
    if len(''.join(emojis)) > max_emojis * 4:
        raise ValidationError(f'{field_name} has too many emojis (max ~{max_emojis}).')
    return value


def explorer_badge(score):
    """Return the short badge name for a given explorer score.

    Delegates to ``gamification.badge_tier_for_score`` so the thresholds
    are defined in exactly one place (``BADGE_TIERS``).
    """
    from .gamification import badge_tier_for_score

    return badge_tier_for_score(score)[2].split()[0]  # e.g. "Bronze" from "Bronze Explorer"


def is_certified_gem(post):
    """Single source-of-truth check for community-certified hidden gems."""
    return (
        post.is_hidden_gem
        and post.gem_votes >= CERTIFIED_GEM_MIN_VOTES
        and post.hidden_gem_score >= CERTIFIED_GEM_MIN_SCORE
    )


def received_likes_count(user):
    """Count of likes received across all of a user's posts."""
    from .models import Like

    return Like.objects.filter(post__author=user).count()


def toggle_instance(model_class, defaults=None, **lookup):
    """Generic create-or-delete toggle.

    Returns ``(instance_or_None, created: bool)``.  When the row already
    existed it is deleted and ``(None, False)`` is returned.
    """
    obj, created = model_class.objects.get_or_create(defaults=defaults, **lookup)
    if not created:
        obj.delete()
        return None, False
    return obj, True


def refresh_user_score(user):
    """Recalculate explorer score and sync achievements for *user*."""
    from .gamification import sync_user_achievements

    user.profile.recalculate_explorer_score()
    return sync_user_achievements(user)

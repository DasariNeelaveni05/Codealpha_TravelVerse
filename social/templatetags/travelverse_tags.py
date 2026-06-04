from django import template

from social.gamification import is_certified_hidden_gem
from social.placeholders import placeholder_for_bucket, placeholder_for_post

register = template.Library()


@register.filter
def gem_score_label(score):
    if score >= 75:
        return 'Elite Gem'
    if score >= 50:
        return 'Rising Gem'
    if score >= 25:
        return 'Hidden Gem'
    return 'New Gem'


@register.filter
def certified_gem(post):
    return is_certified_hidden_gem(post)


@register.simple_tag
def post_image_url(post):
    return placeholder_for_post(post)


@register.simple_tag
def bucket_image_url(item, index=0):
    return placeholder_for_bucket(item, index)

"""
Curated travel placeholder imagery (Unsplash) for empty states and cards without uploads.
"""

# category_key -> image URL
PLACEHOLDER_BY_CATEGORY = {
    'beach': 'https://images.unsplash.com/photo-1507525428034-b723cf961d3e?w=800&q=80',
    'island': 'https://images.unsplash.com/photo-1559127324-4bb0f9115efa?w=800&q=80',
    'mountain': 'https://images.unsplash.com/photo-1464822759023-fed622ff2c3b?w=800&q=80',
    'forest': 'https://images.unsplash.com/photo-1441974231531-c6227db76b6e?w=800&q=80',
    'nature': 'https://images.unsplash.com/photo-1470071459604-3b5ec3a7fe05?w=800&q=80',
    'adventure': 'https://images.unsplash.com/photo-1682687220062-769c9d16f909?w=800&q=80',
    'historical': 'https://images.unsplash.com/photo-1539650116574-75c0cddb8a24?w=800&q=80',
    'cultural': 'https://images.unsplash.com/photo-1528183429752-a97d0bf99f5c?w=800&q=80',
    'food': 'https://images.unsplash.com/photo-1504674900247-0877df9cc836?w=800&q=80',
    'city': 'https://images.unsplash.com/photo-1480714378408-67cf0d13bc1b?w=800&q=80',
    'desert': 'https://images.unsplash.com/photo-1509316785289-025f5b846b8f?w=800&q=80',
    'budget': 'https://images.unsplash.com/photo-1488646953014-85cb44e25828?w=800&q=80',
    'other': 'https://images.unsplash.com/photo-1469854523086-cc02fe5d8800?w=800&q=80',
}

DEFAULT_PLACEHOLDER = PLACEHOLDER_BY_CATEGORY['other']

BUCKET_PLACEHOLDERS = [
    ('https://images.unsplash.com/photo-1559127324-4bb0f9115efa?w=600&q=80', 'tropical'),
    ('https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=600&q=80', 'alps'),
    ('https://images.unsplash.com/photo-1432405972618-c60b0225b8f9?w=600&q=80', 'waterfall'),
    ('https://images.unsplash.com/photo-1516026672322-bc52d61a55d5?w=600&q=80', 'landmark'),
]

DEMO_DESTINATIONS = [
    {'name': 'Secret Lagoon', 'country': 'Iceland', 'lat': 64.255, 'lng': -21.129, 'category': 'nature', 'budget': '$900'},
    {'name': 'Havasu Falls', 'country': 'USA', 'lat': 36.255, 'lng': -112.699, 'category': 'adventure', 'budget': '$600'},
    {'name': 'El Nido', 'country': 'Philippines', 'lat': 11.195, 'lng': 119.405, 'category': 'island', 'budget': '$750'},
    {'name': 'Plitvice Lakes', 'country': 'Croatia', 'lat': 44.865, 'lng': 15.582, 'category': 'forest', 'budget': '$500'},
]


def placeholder_for_post(post):
    if post.primary_image:
        return post.primary_image.url
    cat = getattr(post, 'category', None) or 'other'
    return PLACEHOLDER_BY_CATEGORY.get(cat, DEFAULT_PLACEHOLDER)


def placeholder_for_bucket(item, index=0):
    if item.post and item.post.primary_image:
        return item.post.primary_image.url
    return BUCKET_PLACEHOLDERS[index % len(BUCKET_PLACEHOLDERS)][0]

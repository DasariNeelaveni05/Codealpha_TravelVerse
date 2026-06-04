"""Lat/lng for Leaflet maps — countries and demo destinations."""

COUNTRY_COORDS = {
    'Japan': (35.6762, 139.6503),
    'Italy': (41.8719, 12.5674),
    'Iceland': (64.9631, -19.0208),
    'USA': (37.0902, -95.7129),
    'United States': (37.0902, -95.7129),
    'France': (46.2276, 2.2137),
    'India': (20.5937, 78.9629),
    'Thailand': (15.8700, 100.9925),
    'Greece': (39.0742, 21.8243),
    'Morocco': (31.7917, -7.0926),
    'Peru': (-9.1900, -75.0152),
    'Australia': (-25.2744, 133.7751),
    'South Africa': (-30.5595, 22.9375),
    'Canada': (56.1304, -106.3468),
    'Spain': (40.4637, -3.7492),
    'Indonesia': (-0.7893, 113.9213),
    'Mexico': (23.6345, -102.5528),
    'Egypt': (26.8206, 30.8025),
    'Brazil': (-14.2350, -51.9253),
    'New Zealand': (-40.9006, 174.8860),
    'Croatia': (45.1000, 15.2000),
    'Philippines': (12.8797, 121.7740),
    'Argentina': (-38.4161, -63.6167),
}


def coords_for_post(post):
    if post.latitude and post.longitude:
        return float(post.latitude), float(post.longitude)
    if post.country and post.country in COUNTRY_COORDS:
        return COUNTRY_COORDS[post.country]
    return None


def map_markers_from_posts(posts):
    markers = []
    for post in posts:
        coords = coords_for_post(post)
        if not coords:
            continue
        markers.append({
            'lat': coords[0],
            'lng': coords[1],
            'title': post.location,
            'url': post.get_absolute_url(),
            'score': post.hidden_gem_score,
            'category': post.get_category_display(),
        })
    return markers

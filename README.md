# TravelVerse – Hidden Gems Community

A full-stack Django travel social platform inspired by Instagram, focused on hidden gems, explorer badges, reels, travelogues, and a digital passport.

## Stack

- Django 6 + SQLite
- Django Authentication
- Pillow (image validation)
- HTML, CSS, JavaScript (AJAX feed interactions)

## Setup

```bash
cd Codealpha_Travelverse
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Open http://127.0.0.1:8000/

## Demo data (impressive passport & planner)

After creating a user account:

```bash
python manage.py load_demo_data
python manage.py recalculate_scores
```

This adds sample passport stamps (Japan, Iceland, Italy, etc.), bucket-list destinations, and recalculates gem scores.

## Explorer gamification

- **XP / Explorer Score** from posts, reels, blogs, likes, followers, votes, passport stamps
- **Badges:** Explorer → Bronze Explorer → Silver Backpacker → Gold Nomad → Platinum Traveler
- Progress bar, achievements, and **Travel Statistics** dashboard at `/stats/`

## Features

- Register, login, logout, profile edit with avatar upload
- Travel posts with multiple images, metadata (budget, season, safety, crowd, difficulty, category)
- Itinerary & travel tips, hidden gem voting
- Likes, comments, replies, follow/unfollow (AJAX)
- Bucket list, saved posts, notifications
- Reels, travel blogs/travelogues
- Explorer score & badges (Bronze → Platinum)
- Digital passport (countries/cities from posts)
- Explore trending gems, search users/locations with category filters
- Hidden Gem Score (0–100) on every post; community voting & certification
- Digital passport with world map, timeline, stamps at `/passport/`
- Travel planner bucket list with priorities, dates, progress at `/bucket-list/`
- Infinite scroll feed, double-tap to like
- Three-column responsive layout (nav | feed | widgets)

## Admin

http://127.0.0.1:8000/admin/ — manage all models.

## Project structure

```
travelverse/     # Django project settings
social/          # App: models, views, forms, admin
templates/       # HTML templates
static/          # CSS & JavaScript
media/           # User uploads (created at runtime)
```

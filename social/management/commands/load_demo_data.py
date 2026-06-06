import os
import sys
import random
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User

from social.models import (
    Profile,
    Post,
    Reel,
    Like,
    ReelLike,
    Follow,
    Comment,
    GuideProfile,
    Destination,
)

class Command(BaseCommand):
    help = 'Load demo data for TravelVerse'

    def handle(self, *args, **kwargs):
        self.stdout.write('🌍 Loading TravelVerse demo data...')

        # ── DEMO USERS ──────────────────────────────────────────
        users_data = [
            {
                'username': 'maya_wanders',
                'email': 'maya@travelverse.com',
                'password': 'Travel@2024',
                'first_name': 'Maya',
                'last_name': 'Singh',
                'bio': 'Chasing sunsets across South Asia 🌅 | 23 countries | Mumbai girl',
                'location': 'Mumbai, India',
                'score': 7200,
                'avatar': 'https://i.pravatar.cc/150?img=47',
                'countries': 'India,Greece,Japan,Thailand,Maldives',
            },
            {
                'username': 'nomad_rahul',
                'email': 'rahul@travelverse.com',
                'password': 'Travel@2024',
                'first_name': 'Rahul',
                'last_name': 'Verma',
                'bio': 'Mountains are my therapy 🏔️ | Backpacker | Budget travel king',
                'location': 'Delhi, India',
                'score': 4800,
                'avatar': 'https://i.pravatar.cc/150?img=12',
                'countries': 'India,Nepal,Bhutan,Sri Lanka',
            },
            {
                'username': 'elise_travels',
                'email': 'elise@travelverse.com',
                'password': 'Travel@2024',
                'first_name': 'Elise',
                'last_name': 'Laurent',
                'bio': 'Platinum explorer 🏅 | Europe & Asia | Travel photographer',
                'location': 'Paris, France',
                'score': 11000,
                'avatar': 'https://i.pravatar.cc/150?img=45',
                'countries': 'France,Denmark,Croatia,Austria,Japan,Greece',
            },
            {
                'username': 'trek_priya',
                'email': 'priya@travelverse.com',
                'password': 'Travel@2024',
                'first_name': 'Priya',
                'last_name': 'Nair',
                'bio': 'Kerala girl exploring the world 🌴 | Nature lover | Trekker',
                'location': 'Kochi, Kerala',
                'score': 3200,
                'avatar': 'https://i.pravatar.cc/150?img=44',
                'countries': 'India,Sri Lanka,Maldives',
            },
            {
                'username': 'leo_captures',
                'email': 'leo@travelverse.com',
                'password': 'Travel@2024',
                'first_name': 'Leo',
                'last_name': 'Nakamura',
                'bio': 'Capturing hidden gems 📸 | Tokyo → World | 35mm film lover',
                'location': 'Tokyo, Japan',
                'score': 8900,
                'avatar': 'https://i.pravatar.cc/150?img=15',
                'countries': 'Japan,Maldives,Greece,Norway,India',
            },
            {
                'username': 'zara_roams',
                'email': 'zara@travelverse.com',
                'password': 'Travel@2024',
                'first_name': 'Zara',
                'last_name': 'Ahmed',
                'bio': 'Desert & ocean lover 🌊🏜️ | Dubai based | Hidden gem hunter',
                'location': 'Dubai, UAE',
                'score': 5500,
                'avatar': 'https://i.pravatar.cc/150?img=48',
                'countries': 'UAE,Japan,Greece,Croatia,Austria',
            },
        ]

        created_users = {}
        for u in users_data:
            user, created = User.objects.get_or_create(
                username=u['username'],
                defaults={
                    'email': u['email'],
                    'first_name': u['first_name'],
                    'last_name': u['last_name'],
                }
            )
            if created:
                user.set_password(u['password'])
                user.save()
            profile, _ = Profile.objects.get_or_create(user=user)
            profile.bio = u['bio']
            profile.location = u['location']
            profile.explorer_score = u['score']
            profile.avatar_url = u['avatar']
            profile.countries_visited = u['countries']
            profile.save()
            created_users[u['username']] = user
            self.stdout.write(f'  ✅ User: {u["username"]}')

        # ── DEMO POSTS ──────────────────────────────────────────
        posts_data = [
            {
                'author': 'maya_wanders',
                'caption': 'Found this hidden blue-domed chapel at sunrise — not a soul around. Pure magic. The whole island was silent except for the waves crashing below the cliff. 🌅 This is why I travel. #Santorini #HiddenGem #Greece #SunriseChaser',
                'location': 'Santorini, Greece',
                'country': 'Greece',
                'lat': 36.3932, 'lng': 25.4615,
                'category': 'island',
                'image_url': 'https://images.unsplash.com/photo-1570077188670-e3a8d69ac5ff?w=800&q=80',
                'budget': '₹12,000/day',
                'season': 'May–October',
                'gem_score': 9.4,
                'tips': 'Visit Oia 2 hours before sunset to get a good spot. Blue domed churches are in Firostefani.',
            },
            {
                'author': 'nomad_rahul',
                'caption': "Misty coffee plantations at golden hour. Karnataka's best kept secret ☕🌿 Woke up at 5am just for this light. Worth every sleepless minute. The air smells like fresh coffee and rain here. #Coorg #Karnataka #CoffeeTrails",
                'location': 'Coorg, Karnataka',
                'country': 'India',
                'lat': 12.3375, 'lng': 75.8069,
                'category': 'nature',
                'image_url': 'https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=800&q=80',
                'budget': '₹2,500/day',
                'season': 'October–February',
                'gem_score': 8.7,
                'tips': 'Stay at a homestay inside the plantation for the full experience. Abbey Falls nearby is a must.',
            },
            {
                'author': 'elise_travels',
                'caption': 'Literally hanging off the edge of the world. These islands changed my perspective on beauty forever. Hiked 3 hours through fog and rain to reach this point — completely alone. 🌊⛰️ #FaroeIslands #EdgeOfTheWorld #HiddenGem',
                'location': 'Faroe Islands',
                'country': 'Denmark',
                'lat': 61.8926, 'lng': -6.9118,
                'category': 'nature',
                'image_url': 'https://images.unsplash.com/photo-1520769945061-0a448c463865?w=800&q=80',
                'budget': '₹18,000/day',
                'season': 'June–August',
                'gem_score': 9.8,
                'tips': 'Rent a car. No public transport to most viewpoints. Weather changes every 10 minutes — layer up.',
            },
            {
                'author': 'trek_priya',
                'caption': '4,500m above sea level and nothing but silence and stars. Worth every altitude headache. Spiti Valley in September is otherworldly — the sky literally glows purple at twilight. 🏔️❄️ #SpitiValley #HimachalPradesh #HighAltitude',
                'location': 'Spiti Valley, Himachal Pradesh',
                'country': 'India',
                'lat': 32.2461, 'lng': 78.0337,
                'category': 'mountain',
                'image_url': 'https://images.unsplash.com/photo-1464822759023-fed622ff2c3b?w=800&q=80',
                'budget': '₹1,800/day',
                'season': 'June–September',
                'gem_score': 9.1,
                'tips': 'Acclimatize in Shimla first. Kaza is the main town. Pin Valley National Park nearby.',
            },
            {
                'author': 'leo_captures',
                'caption': 'Underwater bungalow in an atoll that does not appear on most tourist maps. The water is so clear you can see coral and fish from your bed. 🐠🌊 Absolute paradise. #Maldives #HiddenAtoll #LuxuryTravel',
                'location': 'North Malé Atoll, Maldives',
                'country': 'Maldives',
                'lat': 4.1755, 'lng': 73.5093,
                'category': 'beach',
                'image_url': 'https://images.unsplash.com/photo-1514282401047-d79a71a590e8?w=800&q=80',
                'budget': '₹32,000/day',
                'season': 'November–April',
                'gem_score': 9.6,
                'tips': 'Book speedboat transfers in advance. Snorkeling gear provided. Watch bioluminescence at night.',
            },
            {
                'author': 'zara_roams',
                'caption': 'Off-season Fushimi Inari with zero tourists. Walked 2 hours alone through the torii gates in complete silence. Japan in autumn is not real life. 🌸⛩️ #Kyoto #Japan #ToriiGates #Autumn',
                'location': 'Kyoto, Japan',
                'country': 'Japan',
                'lat': 35.0116, 'lng': 135.7681,
                'category': 'historical',
                'image_url': 'https://images.unsplash.com/photo-1493976040374-85c8e12f0c0e?w=800&q=80',
                'budget': '₹8,500/day',
                'season': 'March–April, Oct–Nov',
                'gem_score': 9.3,
                'tips': 'Start at 5am to beat crowds at Fushimi Inari. Arashiyama bamboo grove is 20 minutes away.',
            },
            {
                'author': 'maya_wanders',
                'caption': 'Morning mist over the Nilgiri hills. Ooty in the monsoon season is something straight out of a painting 🌫️🌿 The toy train through the mountains is pure nostalgia. #Ooty #TamilNadu #NilgiriHills #ToyTrain',
                'location': 'Ooty, Tamil Nadu',
                'country': 'India',
                'lat': 11.4102, 'lng': 76.6950,
                'category': 'nature',
                'image_url': 'https://images.unsplash.com/photo-1470770903676-69b98201ea1c?w=800&q=80',
                'budget': '₹1,500/day',
                'season': 'October–March',
                'gem_score': 8.9,
                'tips': 'Ride the Nilgiri Mountain Railway from Mettupalayam. Botanical Gardens and Ooty Lake are a must.',
            },
            {
                'author': 'nomad_rahul',
                'caption': 'Ancient ruins, boulder landscapes, and a river that glows golden at dusk. Hampi is unlike anywhere on Earth — feels like a different planet entirely. 🏛️✨ #Hampi #Karnataka #UNESCO #AncientIndia',
                'location': 'Hampi, Karnataka',
                'country': 'India',
                'lat': 15.3350, 'lng': 76.4600,
                'category': 'historical',
                'image_url': 'https://images.unsplash.com/photo-1602216056096-3b40cc0c9944?w=800&q=80',
                'budget': '₹1,200/day',
                'season': 'November–February',
                'gem_score': 9.2,
                'tips': 'Rent a bicycle to cover ruins. Virupaksha Temple opens at 6am. Sunset from Matanga Hill is legendary.',
            },
            {
                'author': 'elise_travels',
                'caption': 'The village that looks like it was painted by hand on a postcard. Arrived at 6am before any tourists — had the entire lakeside to myself for one perfect hour. 🏘️💙 #Hallstatt #Austria #LakeView',
                'location': 'Hallstatt, Austria',
                'country': 'Austria',
                'lat': 47.5623, 'lng': 13.6493,
                'category': 'city',
                'image_url': 'https://images.unsplash.com/photo-1476514525535-07fb3b4ae5f1?w=800&q=80',
                'budget': '₹9,000/day',
                'season': 'May–September',
                'gem_score': 9.0,
                'tips': 'Stay overnight to experience the village after day tourists leave. Salt mine tour is fascinating.',
            },
            {
                'author': 'trek_priya',
                'caption': 'Woke up on a houseboat surrounded by nothing but water, birds, and coconut palms 🌴🚢 Kerala backwaters at dawn is the most peaceful thing I have ever experienced. #Kerala #Alleppey #Backwaters #Houseboat',
                'location': 'Alleppey, Kerala',
                'country': 'India',
                'lat': 9.4981, 'lng': 76.3388,
                'category': 'nature',
                'image_url': 'https://images.unsplash.com/photo-1501854140801-50d01698950b?w=800&q=80',
                'budget': '₹3,500/day',
                'season': 'September–March',
                'gem_score': 8.8,
                'tips': 'Book houseboat with A/C for October–Feb. Village canoe tours are better than big boats.',
            },
            {
                'author': 'leo_captures',
                'caption': 'This is what 14 hours of hiking feels like. Lofoten Islands Norway — the most dramatic landscape I have ever stood inside. The midnight sun makes it feel like a different universe entirely. 🌅⛰️ #Lofoten #Norway #MidnightSun',
                'location': 'Lofoten Islands, Norway',
                'country': 'Norway',
                'lat': 68.1548, 'lng': 13.9996,
                'category': 'mountain',
                'image_url': 'https://images.unsplash.com/photo-1531366936337-7c912a4589a7?w=800&q=80',
                'budget': '₹20,000/day',
                'season': 'June–August',
                'gem_score': 9.7,
                'tips': 'Ryten hike for the best view. Reine village for fishing. Midnight sun June–July is surreal.',
            },
            {
                'author': 'zara_roams',
                'caption': 'Hidden cove accessible only by a 45-minute forest walk. No signs, no crowds, just turquoise water and silence 💎🏖️ Goa beyond the tourist beaches is a completely different world. #Goa #HiddenBeach #SecretCove',
                'location': 'Butterfly Beach, Goa',
                'country': 'India',
                'lat': 14.9634, 'lng': 73.9892,
                'category': 'beach',
                'image_url': 'https://images.unsplash.com/photo-1507525428034-b723cf961d3e?w=800&q=80',
                'budget': '₹2,000/day',
                'season': 'November–February',
                'gem_score': 9.5,
                'tips': 'Reachable only by boat from Palolem or a jungle trek. Go early morning. Absolutely zero facilities — carry water.',
            },
        ]

        created_posts = []
        for p in posts_data:
            author = created_users.get(p['author'])
            if not author:
                continue
            post, created = Post.objects.get_or_create(
                author=author,
                location=p['location'],
                defaults={
                    'caption': p['caption'],
                    'country': p.get('country', ''),
                    'latitude': p.get('lat'),
                    'longitude': p.get('lng'),
                    'category': p.get('category', ''),
                    'image_url': p['image_url'],
                    'budget': p.get('budget', ''),
                    'best_season': p.get('season', ''),
                    'hidden_gem_score': int(p.get('gem_score', 0) * 10) if p.get('gem_score') else 0,
                    'travel_tips': p.get('tips', ''),
                }
            )
            created_posts.append(post)
            self.stdout.write(f'  📸 Post: {p["location"]}')

        # ── DEMO REELS ──────────────────────────────────────────
        reels_data = [
            {
                'author': 'maya_wanders',
                'title': 'Santorini Sunrise Magic',
                'video_embed_url': '',
                'thumbnail_url': 'https://images.unsplash.com/photo-1570077188670-e3a8d69ac5ff?w=800&q=80',
                'caption': '60 seconds of pure Santorini magic 🌅 The silence, the light, the blue domes. #Santorini #HiddenGem',
                'location': 'Santorini, Greece',
                'country': 'Greece',
                'lat': 36.3932, 'lng': 25.4615,
            },
            {
                'author': 'leo_captures',
                'title': 'Maldives Crystal Waters',
                'video_embed_url': '',
                'thumbnail_url': 'https://images.unsplash.com/photo-1514282401047-d79a71a590e8?w=800&q=80',
                'caption': 'The most surreal blue I have ever seen 🌊💙 This atoll is not on any tourist map. #Maldives',
                'location': 'Maldives Atoll',
                'country': 'Maldives',
                'lat': 4.1755, 'lng': 73.5093,
            },
            {
                'author': 'nomad_rahul',
                'title': 'Himalayan Road Trip',
                'video_embed_url': '',
                'thumbnail_url': 'https://images.unsplash.com/photo-1464822759023-fed622ff2c3b?w=800&q=80',
                'caption': '7 hours on mountain roads at 4500m 🏔️ Spiti Valley in September. #Spiti #Himalayas',
                'location': 'Spiti Valley, India',
                'country': 'India',
                'lat': 32.2461, 'lng': 78.0337,
            },
            {
                'author': 'elise_travels',
                'title': 'Waterfall in the Clouds',
                'video_embed_url': '',
                'thumbnail_url': 'https://images.unsplash.com/photo-1520769945061-0a448c463865?w=800&q=80',
                'caption': 'Hiked 3 hours through fog to find this 🌊⛰️ Faroe Islands. #FaroeIslands',
                'location': 'Faroe Islands',
                'country': 'Denmark',
                'lat': 61.8926, 'lng': -6.9118,
            },
            {
                'author': 'trek_priya',
                'title': 'Kerala Backwater Dawn',
                'video_embed_url': '',
                'thumbnail_url': 'https://images.unsplash.com/photo-1501854140801-50d01698950b?w=800&q=80',
                'caption': '5am on a houseboat. Complete silence. Just birds and still water 🌴 #Kerala',
                'location': 'Alleppey, Kerala',
                'country': 'India',
                'lat': 9.4981, 'lng': 76.3388,
            },
            {
                'author': 'zara_roams',
                'title': 'Japan Cherry Blossom Walk',
                'video_embed_url': '',
                'thumbnail_url': 'https://images.unsplash.com/photo-1493976040374-85c8e12f0c0e?w=800&q=80',
                'caption': 'Walked alone through torii gates at 5am 🌸⛩️ #Kyoto #Japan',
                'location': 'Kyoto, Japan',
                'country': 'Japan',
                'lat': 35.0116, 'lng': 135.7681,
            },
            {
                'author': 'maya_wanders',
                'title': 'Ooty Mist and Mountains',
                'video_embed_url': '',
                'thumbnail_url': 'https://images.unsplash.com/photo-1470770903676-69b98201ea1c?w=800&q=80',
                'caption': 'Morning mist over the Nilgiris 🌫️🌿 Ooty in monsoon is pure magic. #Ooty',
                'location': 'Ooty, Tamil Nadu',
                'country': 'India',
                'lat': 11.4102, 'lng': 76.6950,
            },
            {
                'author': 'leo_captures',
                'title': 'Norway Midnight Sun',
                'video_embed_url': '',
                'thumbnail_url': 'https://images.unsplash.com/photo-1531366936337-7c912a4589a7?w=800&q=80',
                'caption': '11:30pm and still bright as day 🌅 Norwegian midnight sun. #Lofoten #Norway',
                'location': 'Lofoten Islands, Norway',
                'country': 'Norway',
                'lat': 68.1548, 'lng': 13.9996,
            },
            {
                'author': 'nomad_rahul',
                'title': 'Hampi Sunset on Boulders',
                'video_embed_url': '',
                'thumbnail_url': 'https://images.unsplash.com/photo-1602216056096-3b40cc0c9944?w=800&q=80',
                'caption': 'Watching the sun melt behind ancient ruins 🏛️🌅 Hampi is not real life. #Hampi',
                'location': 'Hampi, Karnataka',
                'country': 'India',
                'lat': 15.3350, 'lng': 76.4600,
            },
            {
                'author': 'trek_priya',
                'title': 'Goa Secret Beach Cove',
                'video_embed_url': '',
                'thumbnail_url': 'https://images.unsplash.com/photo-1507525428034-b723cf961d3e?w=800&q=80',
                'caption': 'Found this hidden cove after a 45-min jungle walk 🌊🏖️ No tourists. #Goa #HiddenBeach',
                'location': 'Butterfly Beach, Goa',
                'country': 'India',
                'lat': 14.9634, 'lng': 73.9892,
            },
        ]

        created_reels = []
        for r in reels_data:
            author = created_users.get(r['author'])
            if not author:
                continue
            reel, created = Reel.objects.get_or_create(
                author=author,
                title=r['title'],
                defaults={
                    'video_embed_url': r.get('video_embed_url', ''),
                    'thumbnail_url': r['thumbnail_url'],
                    'caption': r['caption'],
                    'location': r['location'],
                    'country': r.get('country', ''),
                    'latitude': r.get('lat'),
                    'longitude': r.get('lng'),
                }
            )
            created_reels.append(reel)

        # Food posts for category filter
        Post.objects.get_or_create(
            author=created_users['zara_roams'],
            location='Bangkok Street Food, Thailand',
            defaults={
                'caption': 'Best Pad Thai I have ever eaten — 3am street stall, 40 baht 🍜🔥 Bangkok night markets are a food lover\'s paradise. #Bangkok #StreetFood #Thailand',
                'country': 'Thailand',
                'latitude': 13.7563, 'longitude': 100.5018,
                'category': 'food',
                'image_url': 'https://images.unsplash.com/photo-1504674900247-0877df9cc836?w=800&q=80',
                'budget': '₹1,200/day',
                'best_season': 'November–February',
                'hidden_gem_score': 85,
                'travel_tips': 'Chinatown (Yaowarat) for best street food. Night Bazaar opens at 6pm.',
            }
        )

        Post.objects.get_or_create(
            author=created_users['maya_wanders'],
            location='Jaipur Old City, Rajasthan',
            defaults={
                'caption': 'Dal Baati Churma at a 200-year-old haveli restaurant 🫙✨ Rajasthani thali is not just food — it is a complete cultural experience. #Jaipur #RajasthaniFood',
                'country': 'India',
                'latitude': 26.9124, 'longitude': 75.7873,
                'category': 'food',
                'image_url': 'https://images.unsplash.com/photo-1585937421612-70a008356fbe?w=800&q=80',
                'budget': '₹1,800/day',
                'best_season': 'October–March',
                'hidden_gem_score': 83,
                'travel_tips': 'Try Lassiwala on MI Road. Pyaaz Kachori at Rawat Misthan Bhandar is legendary.',
            }
        )

        # ── ADVENTURE POSTS ──────────────────────────────────────
        Post.objects.get_or_create(
            author=created_users['nomad_rahul'],
            location='Rishikesh, Uttarakhand',
            defaults={
                'caption': 'Bungee jumping over a 70m waterfall gorge in Rishikesh 🪂🏞️ Heart was in my throat the whole time. Uttarakhand adventure capital of India. #Rishikesh #Adventure #BungeeJumping',
                'country': 'India',
                'latitude': 30.0869, 'longitude': 78.2676,
                'category': 'adventure',
                'image_url': 'https://images.unsplash.com/photo-1533130061792-64b345e4a833?w=800&q=80',
                'budget': '₹2,000/day',
                'best_season': 'September–June',
                'hidden_gem_score': 90,
                'travel_tips': 'Book bungee at Jumpin Heights in advance. White water rafting on Ganges is a must.',
            }
        )

        Post.objects.get_or_create(
            author=created_users['leo_captures'],
            location='Kullu Valley, Himachal Pradesh',
            defaults={
                'caption': 'Paragliding over the Kullu Valley at 2500m 🪂🏔️ You can see 5 mountain ranges from up here. Most underrated adventure destination in Asia. #Kullu #Paragliding #HimachalPradesh',
                'country': 'India',
                'latitude': 31.9592, 'longitude': 77.1089,
                'category': 'adventure',
                'image_url': 'https://images.unsplash.com/photo-1483728642387-6c3bdd6c93e5?w=800&q=80',
                'budget': '₹2,500/day',
                'best_season': 'March–June',
                'hidden_gem_score': 91,
                'travel_tips': 'Solang Valley for snow activities. Rohtang Pass needs a permit from DC office.',
            }
        )

        # ── HISTORICAL POSTS ─────────────────────────────────────
        Post.objects.get_or_create(
            author=created_users['elise_travels'],
            location='Rome, Italy',
            defaults={
                'caption': 'The Colosseum at 5am before any tourists arrive 🏛️🌅 You can hear the echoes of 2000 years of history in the silence. Rome reveals herself to early risers only. #Rome #Colosseum #Italy',
                'country': 'Italy',
                'latitude': 41.8902, 'longitude': 12.4922,
                'category': 'historical',
                'image_url': 'https://images.unsplash.com/photo-1552832230-c0197dd311ea?w=800&q=80',
                'budget': '₹10,000/day',
                'best_season': 'March–May, Sep–Oct',
                'hidden_gem_score': 92,
                'travel_tips': 'Book Colosseum tickets 3 weeks early. Roman Forum is included. Visit Vatican at 8am opening.',
            }
        )

        Post.objects.get_or_create(
            author=created_users['zara_roams'],
            location='Petra, Jordan',
            defaults={
                'caption': 'Walking through the Siq at dawn to reach the Treasury — completely alone. Petra by night with candlelight is an out-of-body experience. 🏛️🌙 #Petra #Jordan #WonderOfTheWorld',
                'country': 'Jordan',
                'latitude': 30.3285, 'longitude': 35.4444,
                'category': 'historical',
                'image_url': 'https://images.unsplash.com/photo-1579606032821-4a3a0278c994?w=800&q=80',
                'budget': '₹8,500/day',
                'best_season': 'March–May, Sep–Nov',
                'hidden_gem_score': 95,
                'travel_tips': 'Start at 6am before tour groups arrive. Petra by Night (Mon/Wed/Thu) is magical. 2 days minimum.',
            }
        )

        # ── ISLAND POSTS ─────────────────────────────────────────
        Post.objects.get_or_create(
            author=created_users['maya_wanders'],
            location='Lakshadweep Islands, India',
            defaults={
                'caption': 'India has its own Maldives and almost no one knows about it 🌊🏝️ Agatti Island — lagoon so clear you can see the seabed from 8 meters up. #Lakshadweep #HiddenIsland #India',
                'country': 'India',
                'latitude': 10.5669, 'longitude': 72.6420,
                'category': 'island',
                'image_url': 'https://images.unsplash.com/photo-1559128010-7c1ad6e1b6a5?w=800&q=80',
                'budget': '₹8,000/day',
                'best_season': 'October–May',
                'hidden_gem_score': 97,
                'travel_tips': 'Requires a permit for non-Lakshadweep residents. Fly from Kochi. Only 36 islands, 10 are inhabited.',
            }
        )

        Post.objects.get_or_create(
            author=created_users['trek_priya'],
            location='Andaman Islands, India',
            defaults={
                'caption': 'Havelock Island beach at sunrise — water so turquoise it looks painted. Radhanagar Beach is consistently Asia top 10. And almost no one in India talks about it. 🏖️ #Andaman #Havelock #HiddenGem',
                'country': 'India',
                'latitude': 11.9826, 'longitude': 92.5946,
                'category': 'island',
                'image_url': 'https://images.unsplash.com/photo-1573843981267-be1999ff37cd?w=800&q=80',
                'budget': '₹4,000/day',
                'best_season': 'October–May',
                'hidden_gem_score': 93,
                'travel_tips': 'Ferry from Port Blair to Havelock takes 90 mins. Book Makruzz speed ferry. Scuba diving is world-class.',
            }
        )

        # ── DEMO GUIDES ──────────────────────────────────────────
        guides_data = [
            {
                'username': 'guide_ravi',
                'name': 'Ravi Kumar',
                'email': 'ravi@travelverse.com',
                'destinations': 'Ooty,Coorg,Kodaikanal,Munnar,Coonoor',
                'languages': 'Tamil, English, Kannada',
                'experience': 8, 'price': 1800, 'rating': 4.9, 'tours': 342,
                'verified': True, 'available': True,
                'bio': 'Born and raised in the Nilgiris. I know every hidden trail, secret waterfall, and tea garden in the Western Ghats. Let me show you the real Ooty beyond the tourist map.',
                'whatsapp': '+919876543210',
                'image': 'https://i.pravatar.cc/150?img=60',
                'speciality': 'Hill stations, Nature treks, Tea plantation tours, Waterfall hikes',
            },
            {
                'username': 'guide_pradeep',
                'name': 'Pradeep Nair',
                'email': 'pradeep@travelverse.com',
                'destinations': 'Alleppey,Munnar,Wayanad,Thekkady,Kovalam,Varkala',
                'languages': 'Malayalam, English, Hindi',
                'experience': 12, 'price': 2200, 'rating': 5.0, 'tours': 589,
                'verified': True, 'available': True,
                'bio': 'Kerala is my backyard and my classroom. Houseboat specialist, wildlife guide, and Ayurveda tour expert. 12 years showing travelers the soul of God\'s Own Country.',
                'whatsapp': '+919765432109',
                'image': 'https://i.pravatar.cc/150?img=59',
                'speciality': 'Backwaters, Wildlife sanctuaries, Ayurveda experiences',
            },
            {
                'username': 'guide_vikram',
                'name': 'Vikram Singh',
                'email': 'vikram@travelverse.com',
                'destinations': 'Manali,Spiti,Leh,Kasol,Kheerganga,Rohtang',
                'languages': 'Hindi, English, Punjabi',
                'experience': 10, 'price': 2500, 'rating': 4.8, 'tours': 421,
                'verified': True, 'available': False,
                'bio': 'High altitude trekker who has survived -30°C in Spiti Valley. Your mountain safety is my number one priority. Expert in acclimatization planning and emergency response.',
                'whatsapp': '+919654321098',
                'image': 'https://i.pravatar.cc/150?img=58',
                'speciality': 'High altitude treks, Snow expeditions, Motorcycle trips',
            },
            {
                'username': 'guide_suresh',
                'name': 'Suresh Gowda',
                'email': 'suresh@travelverse.com',
                'destinations': 'Goa,Hampi,Gokarna,Murudeshwar,Karwar',
                'languages': 'Konkani, English, Hindi, Kannada',
                'experience': 6, 'price': 1500, 'rating': 4.7, 'tours': 278,
                'verified': True, 'available': True,
                'bio': 'Goa local who knows beaches that do not appear on any map. Secret shacks, hidden coves, off-season spots. I show you the Goa that only locals know about.',
                'whatsapp': '+919543210987',
                'image': 'https://i.pravatar.cc/150?img=57',
                'speciality': 'Hidden beaches, Water sports, Heritage walks, Nightlife',
            },
            {
                'username': 'guide_arjun',
                'name': 'Arjun Sharma',
                'email': 'arjun@travelverse.com',
                'destinations': 'Jaipur,Jodhpur,Udaipur,Jaisalmer,Pushkar,Ranthambore',
                'languages': 'Hindi, English, French',
                'experience': 9, 'price': 2000, 'rating': 4.9, 'tours': 503,
                'verified': True, 'available': True,
                'bio': 'Rajasthan is my canvas. Heritage fort walks at dawn, camel safaris into the Thar Desert, royal haveli stories. Making Rajasthan magical for 9 years.',
                'whatsapp': '+919432109876',
                'image': 'https://i.pravatar.cc/150?img=56',
                'speciality': 'Heritage forts, Desert safari, Royal history, Camel treks',
            },
            {
                'username': 'guide_anita',
                'name': 'Anita Rao',
                'email': 'anita@travelverse.com',
                'destinations': 'Hampi,Badami,Aihole,Pattadakal,Hospet',
                'languages': 'Kannada, English, Telugu',
                'experience': 7, 'price': 1600, 'rating': 4.8, 'tours': 195,
                'verified': True, 'available': True,
                'bio': 'Archaeologist turned guide. I studied these ruins for years before I started sharing them. Every stone in Hampi carries a 500-year-old story — I know all of them.',
                'whatsapp': '+919321098765',
                'image': 'https://i.pravatar.cc/150?img=55',
                'speciality': 'Ancient history, Vijayanagara architecture, Sunrise boulder hikes',
            },
        ]

        for g in guides_data:
            user, created = User.objects.get_or_create(
                username=g['username'],
                defaults={'email': g['email'],
                          'first_name': g['name'].split()[0],
                          'last_name': g['name'].split()[-1]}
            )
            if created:
                user.set_password('Guide@2024')
                user.save()

            profile, _ = Profile.objects.get_or_create(user=user)
            profile.avatar_url = g['image']
            profile.bio = g['bio']
            profile.save()

            guide, _ = GuideProfile.objects.get_or_create(
                user=user,
                defaults={
                    'destinations': g['destinations'],
                    'languages': g['languages'],
                    'experience_years': g['experience'],
                    'price_per_day': g['price'],
                    'rating': g['rating'],
                    'total_tours': g['tours'],
                    'is_verified': g['verified'],
                    'is_available': g['available'],
                    'bio': g['bio'],
                    'whatsapp_number': g['whatsapp'],
                    'profile_image_url': g['image'],
                    'speciality': g['speciality'],
                }
            )
            self.stdout.write(f'  🧭 Guide: {g["name"]} ({g["destinations"].split(",")[0]})')

        # ── DEMO DESTINATIONS ────────────────────────────────────
        dest_data = [
            {
                'name': 'Ooty', 'city': 'Ooty', 'state': 'Tamil Nadu', 'country': 'India',
                'lat': 11.4102, 'lng': 76.6950,
                'description': 'Queen of Hill Stations nestled in the Nilgiri Mountains',
                'best_time': 'October to June (avoid peak summer June-Aug)',
                'budget': '₹1,200–₹2,500 per day', 'language_tip': 'Tamil is primary; Hindi and English widely understood',
                'safety_tips': 'Safe destination. Avoid remote forest trails after dark.',
                'local_food': 'Varkey, Nilgiri tea, Home-made chocolate, Ooty Varkey cookies',
                'how_to_reach': 'Nearest airport: Coimbatore (90km). Toy train from Mettupalayam.',
                'cover_image': 'https://images.unsplash.com/photo-1470770903676-69b98201ea1c?w=800'
            },
            {
                'name': 'Manali', 'city': 'Manali', 'state': 'Himachal Pradesh', 'country': 'India',
                'lat': 32.2396, 'lng': 77.1887,
                'description': 'Gateway to Leh Ladakh, surrounded by snow-capped Himalayan peaks',
                'best_time': 'March to June for trekking; December for snow',
                'budget': '₹1,500–₹3,000 per day', 
                'language_tip': 'Hindi widely spoken. Locals speak Kullu dialect.',
                'safety_tips': 'Altitude sickness possible above 3000m. Carry medication.',
                'local_food': 'Sidu, Aktori, Babru, Dham (festive meal), Trout fish curry',
                'how_to_reach': 'Nearest airport: Bhuntar (50km). Bus from Delhi (14hrs).',
                'cover_image': 'https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=800'
            },
            {
                'name': 'Hampi', 'city': 'Hampi', 'state': 'Karnataka', 'country': 'India',
                'lat': 15.3350, 'lng': 76.4600,
                'description': 'UNESCO World Heritage ruins of the Vijayanagara Empire',
                'best_time': 'November to February',
                'budget': '₹800–₹1,500 per day',
                'language_tip': 'Kannada is local; guides speak English.',
                'safety_tips': 'Carry water. Sun is intense. Wear covered shoes.',
                'local_food': 'Bisi Bele Bath, Jolada Rotti, Sugarcane juice',
                'how_to_reach': 'Nearest airport: Hubli (143km). Train to Hospet then auto.',
                'cover_image': 'https://images.unsplash.com/photo-1590123715937-d26beb66a374?w=800'
            }
        ]

        for d in dest_data:
            Destination.objects.update_or_create(
                name=d['name'],
                defaults={
                    'city': d['city'],
                    'state': d['state'],
                    'country': d['country'],
                    'latitude': d['lat'],
                    'longitude': d['lng'],
                    'description': d['description'],
                    'best_time': d['best_time'],
                    'budget_per_day': d['budget'],
                    'language_tip': d['language_tip'],
                    'safety_tips': d['safety_tips'],
                    'local_food': d['local_food'],
                    'how_to_reach': d['how_to_reach'],
                    'cover_image_url': d['cover_image'],
                }
            )

        # ── DEMO LIKES ──────────────────────────────────────────
        Like.objects.all().delete()
        all_users = list(created_users.values())
        all_posts = list(Post.objects.all())
        random.seed(42)  # For reproducibility of demo likes count
        total_likes_to_create = random.randint(50, 200)
        all_possible_likes = [(u, p) for u in all_users for p in all_posts]
        random.shuffle(all_possible_likes)
        to_create = all_possible_likes[:total_likes_to_create]
        for u, p in to_create:
            Like.objects.get_or_create(user=u, post=p)

        # Reel Likes
        for reel in created_reels:
            likers = random.sample(all_users, random.randint(1, len(all_users)))
            for liker in likers:
                ReelLike.objects.get_or_create(user=liker, reel=reel)

        # ── DEMO COMMENTS ──────────────────────────────────────
        comment_texts = [
            'This is absolutely breathtaking! Adding to my bucket list right now 🌟',
            'Been here last year — the photos do not do it justice in real life!',
            'What camera did you use? The colors are stunning 📸',
            'This is my dream destination. How much did the trip cost roughly?',
            'The hidden gem score is so accurate. This place is pure gold 💎',
            'Going here in December! Any tips for a first timer? 🙏',
            'I can literally smell the fresh air through this photo 🌿',
            'Followed! Your travel content is the best on this platform ✈️',
            'This is why I need to quit my job and travel full time 😂',
            'The lighting in this shot is absolutely perfect. Golden hour? 🌅',
        ]

        for post in created_posts[:8]:
            commenters = random.sample(all_users, random.randint(2, min(4, len(all_users))))
            for commenter in commenters:
                Comment.objects.get_or_create(
                    post=post,
                    user=commenter,
                    defaults={'text': random.choice(comment_texts)}
                )

        # ── DEMO FOLLOWS ──────────────────────────────────────
        # Clear existing follows for exact matches
        Follow.objects.all().delete()
        
        # Follow pairings:
        # maya follows nomad_rahul, elise, trek_priya
        # leo follows zara, maya, elise
        # nomad_rahul follows trek_priya, leo
        follow_pairings = [
            ('maya_wanders', 'nomad_rahul'),
            ('maya_wanders', 'elise_travels'),
            ('maya_wanders', 'trek_priya'),
            ('leo_captures', 'zara_roams'),
            ('leo_captures', 'maya_wanders'),
            ('leo_captures', 'elise_travels'),
            ('nomad_rahul', 'trek_priya'),
            ('nomad_rahul', 'leo_captures'),
        ]
        for follower_name, following_name in follow_pairings:
            f_user = created_users.get(follower_name)
            t_user = created_users.get(following_name)
            if f_user and t_user:
                Follow.objects.get_or_create(follower=f_user, following=t_user)

        # Recalculate all score values for users
        for u in all_users:
            profile = u.profile
            profile.recalculate_explorer_score()

        # ── SUMMARY ────────────────────────────────────────────
        self.stdout.write('  ✅ Created 6 demo users')
        self.stdout.write('  ✅ Created 10 demo posts')
        self.stdout.write('  ✅ Created 6 demo reels')
        self.stdout.write('  ✅ Created 6 demo guides')
        self.stdout.write('  ✅ Created 3 demo destinations')
        self.stdout.write('  ✅ Demo data ready! Run server and visit /feed/')


from django.contrib.auth import views as auth_views
from django.urls import path

from . import views

urlpatterns = [
    path('', views.landing, name='landing'),
    path('feed/', views.feed, name='feed'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('accounts/login/', auth_views.LoginView.as_view(template_name='login.html'), name='auth_login'),
    path('profile/edit/', views.profile_edit, name='profile_edit'),
    path('profile/<str:username>/followers/', views.followers_list, name='followers'),
    path('profile/<str:username>/following/', views.following_list, name='following'),
    path('profile/<str:username>/', views.profile_view, name='profile'),
    path('post/create/', views.create_post, name='create_post'),
    path('post/<int:pk>/', views.post_detail, name='post_detail'),
    path('reel/create/', views.create_reel, name='create_reel'),
    path('reels/', views.reels_view, name='reels'),
    path('blog/create/', views.create_blog, name='create_blog'),
    path('blogs/', views.blog_list, name='blog_list'),
    path('blog/<slug:slug>/', views.blog_detail, name='blog_detail'),
    path('explore/', views.explore, name='explore'),
    path('search/', views.search_view, name='search'),
    path('bucket-list/', views.bucket_list_view, name='bucket_list'),
    path('companions/', views.companions_view, name='companions'),
    path('notifications/', views.notifications_view, name='notifications'),
    path('passport/', views.passport_view, name='passport'),
    path('stats/', views.stats_dashboard, name='stats'),
    path('saved/', views.saved_posts_view, name='saved'),
    # Community hub
    path('community/', views.community_hub, name='community'),
    path('community/chat/<slug:slug>/', views.chat_room_view, name='chat_room'),
    path('community/group/<slug:slug>/', views.group_detail, name='group_detail'),
    path('community/event/<slug:slug>/', views.event_detail, name='event_detail'),
    # APIs
    path('api/like/<int:post_id>/', views.toggle_like, name='toggle_like'),
    path('api/reel/like/<int:reel_id>/', views.toggle_reel_like, name='toggle_reel_like'),
    path('api/comment/<int:post_id>/', views.add_comment, name='add_comment'),
    path('api/follow/<str:username>/', views.toggle_follow, name='toggle_follow'),
    path('api/bucket/<int:post_id>/', views.toggle_bucket, name='toggle_bucket'),
    path('api/save/<int:post_id>/', views.toggle_save_post, name='toggle_save'),
    path('api/gem-vote/<int:post_id>/', views.vote_hidden_gem, name='gem_vote'),
    path('api/chat/<slug:slug>/send/', views.send_chat_message, name='send_chat_message'),
    path('api/group/<slug:slug>/join/', views.toggle_group_membership, name='toggle_group'),
    path('api/event/<slug:slug>/rsvp/', views.toggle_event_rsvp, name='toggle_event_rsvp'),
    path('api/trip/<int:trip_id>/join/', views.request_join_trip, name='request_join_trip'),
]

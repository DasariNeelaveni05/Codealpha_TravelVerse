from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User

from .models import (
    Blog,
    BucketList,
    Collection,
    CollectionItem,
    Comment,
    Destination,
    Follow,
    GuideProfile,
    GuideRequest,
    HiddenGemVote,
    Itinerary,
    ItineraryItem,
    Like,
    Notification,
    PassportStamp,
    Post,
    PostImage,
    Profile,
    Reaction,
    Reel,
    ReelLike,
    SavedPost,
    TravelCompanion,
    UserAchievement,
)


class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False


class UserAdmin(BaseUserAdmin):
    inlines = (ProfileInline,)


class PostImageInline(admin.TabularInline):
    model = PostImage
    extra = 1


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('id', 'author', 'location', 'category', 'is_hidden_gem', 'gem_votes', 'created_at')
    list_filter = ('category', 'is_hidden_gem', 'difficulty', 'crowd_level')
    search_fields = ('caption', 'location', 'city', 'country', 'hidden_gem_description', 'author__username')
    inlines = [PostImageInline]


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'explorer_score', 'location', 'created_at')
    search_fields = ('user__username', 'bio', 'location')


@admin.register(Reel)
class ReelAdmin(admin.ModelAdmin):
    list_display = ('id', 'author', 'location', 'created_at')
    search_fields = ('caption', 'location', 'author__username')


@admin.register(Blog)
class BlogAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'location', 'created_at')
    prepopulated_fields = {'slug': ('title',)}
    search_fields = ('title', 'content', 'author__username')


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('user', 'post', 'parent', 'created_at')
    search_fields = ('text', 'user__username')


@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ('user', 'post', 'created_at')


@admin.register(ReelLike)
class ReelLikeAdmin(admin.ModelAdmin):
    list_display = ('user', 'reel', 'created_at')


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = ('follower', 'following', 'created_at')


@admin.register(BucketList)
class BucketListAdmin(admin.ModelAdmin):
    list_display = ('user', 'destination_name', 'priority', 'planned_date', 'added_at')
    list_filter = ('priority',)


@admin.register(SavedPost)
class SavedPostAdmin(admin.ModelAdmin):
    list_display = ('user', 'post', 'saved_at')


@admin.register(HiddenGemVote)
class HiddenGemVoteAdmin(admin.ModelAdmin):
    list_display = ('user', 'post', 'created_at')


@admin.register(PassportStamp)
class PassportAdmin(admin.ModelAdmin):
    list_display = ('user', 'city', 'state', 'country', 'visited_at')


@admin.register(TravelCompanion)
class TravelCompanionAdmin(admin.ModelAdmin):
    list_display = ('user', 'destination', 'country', 'start_date', 'is_active')
    list_filter = ('is_active',)


@admin.register(UserAchievement)
class UserAchievementAdmin(admin.ModelAdmin):
    list_display = ('user', 'key', 'unlocked_at')
    list_filter = ('key',)


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('recipient', 'actor', 'notification_type', 'is_read', 'created_at')
    list_filter = ('notification_type', 'is_read')


admin.site.unregister(User)
admin.site.register(User, UserAdmin)


@admin.register(GuideProfile)
class GuideProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'rating', 'total_tours', 'experience_years', 'availability_status')
    list_filter = ('availability_status',)
    search_fields = ('user__username', 'bio', 'destination_expertise')


@admin.register(GuideRequest)
class GuideRequestAdmin(admin.ModelAdmin):
    list_display = ('user', 'destination', 'start_date', 'group_size', 'is_open')
    list_filter = ('is_open',)


@admin.register(Destination)
class DestinationAdmin(admin.ModelAdmin):
    list_display = ('name', 'country', 'crowd_level', 'safety_rating', 'budget_tier')
    search_fields = ('name', 'country')


@admin.register(Itinerary)
class ItineraryAdmin(admin.ModelAdmin):
    list_display = ('user', 'title', 'destination_name', 'days_count', 'start_date')
    search_fields = ('title', 'destination_name', 'user__username')


@admin.register(ItineraryItem)
class ItineraryItemAdmin(admin.ModelAdmin):
    list_display = ('itinerary', 'day_number', 'time_block', 'activity', 'order')


@admin.register(Collection)
class CollectionAdmin(admin.ModelAdmin):
    list_display = ('user', 'name', 'created_at')


@admin.register(CollectionItem)
class CollectionItemAdmin(admin.ModelAdmin):
    list_display = ('collection', 'post', 'added_at')


@admin.register(Reaction)
class ReactionAdmin(admin.ModelAdmin):
    list_display = ('user', 'post', 'reaction_type', 'created_at')
    list_filter = ('reaction_type',)


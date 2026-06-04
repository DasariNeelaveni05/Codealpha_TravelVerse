import re

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

from .models import Blog, BucketList, Comment, Post, Profile, Reel, TravelCompanion
from .utils import validate_image_upload, validate_text_with_emojis, validate_video_upload

USERNAME_PATTERN = re.compile(r'^[a-zA-Z0-9_]{3,30}$')


class SignUpForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'explorer_username',
                'autocomplete': 'username',
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'you@email.com',
                'autocomplete': 'email',
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Strong password',
            'autocomplete': 'new-password',
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Confirm password',
            'autocomplete': 'new-password',
        })
        self.fields['username'].help_text = (
            '3–30 characters. Letters, numbers, and underscores only.'
        )
        self.fields['password1'].help_text = (
            'At least 8 characters. Avoid common passwords and personal info.'
        )

    def clean_username(self):
        username = self.cleaned_data.get('username', '').strip()
        if not USERNAME_PATTERN.match(username):
            raise ValidationError(
                'Username must be 3–30 characters and use only letters, numbers, and underscores.'
            )
        if User.objects.filter(username__iexact=username).exists():
            raise ValidationError('This username is already taken.')
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email', '').strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise ValidationError('An account with this email already exists.')
        return email

    def clean(self):
        cleaned = super().clean()
        p1 = cleaned.get('password1')
        p2 = cleaned.get('password2')
        if p1 and p2 and p1 != p2:
            raise ValidationError('Passwords do not match. Please re-enter them.')
        return cleaned

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user


class ProfileEditForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ('bio', 'avatar', 'location', 'website')
        widgets = {
            'bio': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Tell explorers about your journeys...',
            }),
            'location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Home base'}),
            'website': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://'}),
        }

    def clean_bio(self):
        return validate_text_with_emojis(self.cleaned_data.get('bio', ''), 'Bio', 500, 30)

    def clean_avatar(self):
        avatar = self.cleaned_data.get('avatar')
        if avatar:
            validate_image_upload(avatar)
        return avatar


class PostForm(forms.ModelForm):
    budget_slider = forms.IntegerField(
        min_value=0,
        max_value=10000,
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'budget-slider',
            'type': 'range',
            'min': '0',
            'max': '10000',
            'step': '50',
        }),
        label='Trip budget (USD)',
    )

    class Meta:
        model = Post
        fields = [
            'caption', 'location', 'city', 'state', 'country',
            'best_season', 'safety_rating', 'crowd_level', 'difficulty',
            'category', 'itinerary', 'travel_tips', 'hidden_gem_description',
            'is_hidden_gem',
        ]
        widgets = {
            'caption': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Share your travel story...',
            }),
            'location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Secret waterfall, Bali'}),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
            'state': forms.TextInput(attrs={'class': 'form-control'}),
            'country': forms.TextInput(attrs={'class': 'form-control'}),
            'best_season': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Oct – Mar'}),
            'itinerary': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'travel_tips': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'hidden_gem_description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Why is this a hidden gem?',
            }),
            'safety_rating': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 5}),
            'crowd_level': forms.Select(attrs={'class': 'form-control'}),
            'difficulty': forms.Select(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'is_hidden_gem': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def clean_caption(self):
        return validate_text_with_emojis(self.cleaned_data.get('caption', ''), 'Caption', 2200, 40)

    def clean_location(self):
        loc = (self.cleaned_data.get('location') or '').strip()
        if not loc:
            raise ValidationError('Location is required.')
        return loc

    def save(self, commit=True):
        post = super().save(commit=False)
        amount = self.cleaned_data.get('budget_slider')
        if amount:
            post.budget_amount = amount
            post.budget = f'${amount:,}'
        if commit:
            post.save()
            self.save_m2m()
        return post


class ReelForm(forms.ModelForm):
    class Meta:
        model = Reel
        fields = ('video', 'caption', 'location')
        widgets = {
            'caption': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def clean_video(self):
        video = self.cleaned_data.get('video')
        validate_video_upload(video)
        return video

    def clean_caption(self):
        return validate_text_with_emojis(self.cleaned_data.get('caption', ''), 'Caption', 500, 20)


class BlogForm(forms.ModelForm):
    class Meta:
        model = Blog
        fields = ('title', 'content', 'cover_image', 'location', 'budget', 'itinerary', 'recommendations')
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'My journey to...'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 10}),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
            'budget': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '$500–$1200'}),
            'itinerary': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'recommendations': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }

    def clean_cover_image(self):
        img = self.cleaned_data.get('cover_image')
        if img:
            validate_image_upload(img)
        return img


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)
        widgets = {
            'text': forms.TextInput(attrs={
                'placeholder': 'Add a comment...',
                'class': 'comment-input form-control',
            }),
        }

    def clean_text(self):
        return validate_text_with_emojis(self.cleaned_data.get('text', ''), 'Comment', 1000, 25)


class BucketListForm(forms.ModelForm):
    class Meta:
        model = BucketList
        fields = (
            'destination_name', 'notes', 'planned_date', 'reminder_date', 'priority',
            'travel_goal', 'progress', 'status', 'cover_theme',
        )
        widgets = {
            'destination_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Santorini, Greece',
            }),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'planned_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'reminder_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'priority': forms.Select(attrs={'class': 'form-control'}),
            'cover_theme': forms.Select(
                attrs={'class': 'form-control'},
                choices=[
                    ('', 'Auto theme'),
                    ('beach', 'Beach'),
                    ('mountain', 'Mountains'),
                    ('island', 'Island'),
                    ('nature', 'Nature'),
                    ('adventure', 'Adventure'),
                ],
            ),
            'travel_goal': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Hiking & photography'}),
            'progress': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'max': 100}),
            'status': forms.Select(attrs={'class': 'form-control'}),
        }


class TravelCompanionForm(forms.ModelForm):
    class Meta:
        model = TravelCompanion
        fields = ('destination', 'country', 'start_date', 'end_date', 'description', 'budget_range')
        widgets = {
            'destination': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Bali, Indonesia'}),
            'country': forms.TextInput(attrs={'class': 'form-control'}),
            'start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'end_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'budget_range': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '$500–$1000'}),
        }

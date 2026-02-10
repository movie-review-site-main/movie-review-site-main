from django.contrib import admin
from .models import UserProfile, Movie, Rating, Review, Comment

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'created_at']
    search_fields = ['user__username', 'bio']
    list_filter = ['created_at']

@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    list_display = ['title', 'genre', 'director', 'release_date', 'average_rating', 'created_at']
    search_fields = ['title', 'director', 'description']
    list_filter = ['genre', 'release_date', 'created_at']
    date_hierarchy = 'release_date'

@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
    list_display = ['user', 'movie', 'rating', 'created_at']
    search_fields = ['user__username', 'movie__title']
    list_filter = ['rating', 'created_at']

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'movie', 'created_at']
    search_fields = ['title', 'content', 'user__username', 'movie__title']
    list_filter = ['created_at', 'updated_at']
    date_hierarchy = 'created_at'

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['user', 'review', 'created_at']
    search_fields = ['content', 'user__username']
    list_filter = ['created_at']
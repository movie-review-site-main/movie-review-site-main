from rest_framework import serializers
from .models import Movie, Rating, Review, Comment

class MovieSerializer(serializers.ModelSerializer):
    average_rating = serializers.SerializerMethodField()
    
    class Meta:
        model = Movie
        fields = ['id', 'title', 'description', 'genre', 'release_date', 
                  'director', 'poster', 'created_at', 'average_rating']
    
    def get_average_rating(self, obj):
        return obj.average_rating()

class RatingSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField()
    movie = serializers.StringRelatedField()
    
    class Meta:
        model = Rating
        fields = ['id', 'movie', 'user', 'rating', 'created_at']

class ReviewSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField()
    movie = serializers.StringRelatedField()
    
    class Meta:
        model = Review
        fields = ['id', 'movie', 'user', 'title', 'content', 'created_at', 'updated_at']

class CommentSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField()
    
    class Meta:
        model = Comment
        fields = ['id', 'review', 'user', 'content', 'created_at']
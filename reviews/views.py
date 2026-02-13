from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Avg, Count
from .models import Movie, Rating, Review, Comment, UserProfile
from .forms import UserRegisterForm, UserProfileForm, MovieForm, RatingForm, ReviewForm, CommentForm

def home(request):
    # Основные фильмы (топ 6)
    movies = Movie.objects.annotate(
        avg_rating=Avg('ratings__rating')
    ).order_by('-avg_rating')[:6]

    # Топ 10
    top_rated = Movie.objects.annotate(
        avg_rating=Avg('ratings__rating')
    ).order_by('-avg_rating')[:10]

    # Последние отзывы
    recent_reviews = Review.objects.select_related(
        'user', 'movie'
    ).order_by('-created_at')[:5]

    # --- РЕКОМЕНДАЦИИ ---
    recommended_movies = None

    if request.user.is_authenticated:
        user_ratings = Rating.objects.filter(user=request.user)

        if user_ratings.exists():
            favorite_genres = Movie.objects.filter(
                ratings__in=user_ratings
            ).values_list('genre', flat=True)

            recommended_movies = Movie.objects.filter(
                genre__in=favorite_genres
            ).exclude(
                ratings__user=request.user
            ).annotate(
                avg_rating=Avg('ratings__rating')
            ).order_by('-avg_rating')[:5]

    context = {
        'movies': movies,
        'top_rated': top_rated,
        'recent_reviews': recent_reviews,
        'recommended_movies': recommended_movies,
    }

    return render(request, 'reviews/home.html', context)


def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            UserProfile.objects.create(user=user)
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}!')
            login(request, user)
            return redirect('home')
    else:
        form = UserRegisterForm()
    return render(request, 'reviews/register.html', {'form': form})


@login_required
def profile(request):
    profile, created = UserProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile has been updated!')
            return redirect('profile')
    else:
        form = UserProfileForm(instance=profile)

    user_reviews = Review.objects.filter(user=request.user).select_related('movie')
    user_ratings = Rating.objects.filter(user=request.user).select_related('movie')

    context = {
        'form': form,
        'user_reviews': user_reviews,
        'user_ratings': user_ratings,
    }
    return render(request, 'reviews/profile.html', context)


def movie_list(request):
    movies = Movie.objects.annotate(avg_rating=Avg('ratings__rating')).order_by('-created_at')

    genre = request.GET.get('genre')
    if genre:
        movies = movies.filter(genre=genre)

    year = request.GET.get('year')
    if year:
        movies = movies.filter(release_date__year=year)

    years = Movie.objects.dates('release_date', 'year', order='DESC')

    context = {
        'movies': movies,
        'years': years,
        'current_year': year,
    }
    return render(request, 'reviews/movie_list.html', context)


def movie_detail(request, pk):
    movie = get_object_or_404(Movie, pk=pk)
    reviews = movie.reviews.select_related('user').all()
    user_rating = None

    if request.user.is_authenticated:
        user_rating = Rating.objects.filter(movie=movie, user=request.user).first()

    context = {
        'movie': movie,
        'reviews': reviews,
        'user_rating': user_rating,
    }
    return render(request, 'reviews/movie_detail.html', context)


@login_required
def add_movie(request):
    if request.method == 'POST':
        form = MovieForm(request.POST, request.FILES)
        if form.is_valid():
            movie = form.save(commit=False)
            movie.created_by = request.user
            movie.save()
            messages.success(request, 'Movie added successfully!')
            return redirect('movie_detail', pk=movie.pk)
    else:
        form = MovieForm()
    return render(request, 'reviews/add_movie.html', {'form': form})


@login_required
def add_rating(request, movie_id):
    movie = get_object_or_404(Movie, pk=movie_id)

    if request.method == 'POST':
        form = RatingForm(request.POST)
        if form.is_valid():
            rating, created = Rating.objects.update_or_create(
                movie=movie,
                user=request.user,
                defaults={'rating': form.cleaned_data['rating']}
            )
            messages.success(request, 'Rating saved!')
            return redirect('movie_detail', pk=movie_id)
    else:
        existing_rating = Rating.objects.filter(movie=movie, user=request.user).first()
        form = RatingForm(instance=existing_rating)

    return render(request, 'reviews/add_rating.html', {'form': form, 'movie': movie})


@login_required
def add_review(request, movie_id):
    movie = get_object_or_404(Movie, pk=movie_id)

    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.movie = movie
            review.user = request.user
            review.save()
            messages.success(request, 'Review posted!')
            return redirect('movie_detail', pk=movie_id)
    else:
        form = ReviewForm()

    return render(request, 'reviews/add_review.html', {'form': form, 'movie': movie})


@login_required
def add_comment(request, review_id):
    review = get_object_or_404(Review, pk=review_id)

    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.review = review
            comment.user = request.user
            comment.save()
            messages.success(request, 'Comment added!')
            return redirect('movie_detail', pk=review.movie.pk)

    return redirect('movie_detail', pk=review.movie.pk)


def top_rated(request):
    movies = Movie.objects.annotate(
        avg_rating=Avg('ratings__rating'),
        rating_count=Count('ratings')
    ).filter(rating_count__gte=1).order_by('-avg_rating')[:20]

    context = {'movies': movies}
    return render(request, 'reviews/top_rated.html', context)


from rest_framework import generics
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .serializers import MovieSerializer, RatingSerializer, ReviewSerializer


class MovieListAPI(generics.ListCreateAPIView):
    queryset = Movie.objects.all()
    serializer_class = MovieSerializer


class MovieDetailAPI(generics.RetrieveAPIView):
    queryset = Movie.objects.all()
    serializer_class = MovieSerializer


class RatingListAPI(generics.ListCreateAPIView):
    queryset = Rating.objects.all()
    serializer_class = RatingSerializer


class ReviewListAPI(generics.ListCreateAPIView):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer


@api_view(['GET'])
def top_rated_api(request):
    movies = Movie.objects.annotate(
        avg_rating=Avg('ratings__rating')
    ).order_by('-avg_rating')[:10]

    serializer = MovieSerializer(movies, many=True)
    return Response(serializer.data)

@login_required
def recommendations(request):
    user_ratings = Rating.objects.filter(user=request.user).select_related('movie')

    if not user_ratings.exists():
        recommended_movies = Movie.objects.annotate(
            avg_rating=Avg('ratings__rating'),
            rating_count=Count('ratings')
        ).filter(rating_count__gte=1).order_by('-avg_rating')[:10]

        context = {
            'recommended_movies': recommended_movies,
            'has_ratings': False,
        }
        return render(request, 'reviews/recommendations.html', context)

    favorite_genres = user_ratings.filter(
        rating__gte=7
    ).values_list('movie__genre', flat=True)

    rated_movie_ids = user_ratings.values_list('movie_id', flat=True)

    recommended_movies = Movie.objects.filter(
        genre__in=favorite_genres
    ).exclude(
        id__in=rated_movie_ids
    ).annotate(
        avg_rating=Avg('ratings__rating')
    ).order_by('-avg_rating')[:10]

    context = {
        'recommended_movies': recommended_movies,
        'has_ratings': True,
    }

    return render(request, 'reviews/recommendations.html', context)

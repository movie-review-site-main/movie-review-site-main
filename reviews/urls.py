from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # Main pages
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='reviews/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('profile/', views.profile, name='profile'),
    
    # Movies
    path('movies/', views.movie_list, name='movie_list'),
    path('movie/<int:pk>/', views.movie_detail, name='movie_detail'),
    path('movie/add/', views.add_movie, name='add_movie'),
    path('top-rated/', views.top_rated, name='top_rated'),
    
    # Ratings and Reviews
    path('movie/<int:movie_id>/rate/', views.add_rating, name='add_rating'),
    path('movie/<int:movie_id>/review/', views.add_review, name='add_review'),
    path('review/<int:review_id>/comment/', views.add_comment, name='add_comment'),
    
    # API endpoints
    path('api/movies/', views.MovieListAPI.as_view(), name='api_movie_list'),
    path('api/movies/<int:pk>/', views.MovieDetailAPI.as_view(), name='api_movie_detail'),
    path('api/ratings/', views.RatingListAPI.as_view(), name='api_rating_list'),
    path('api/reviews/', views.ReviewListAPI.as_view(), name='api_review_list'),
    path('api/top-rated/', views.top_rated_api, name='api_top_rated'),
]
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),  # Home view
    path('playlist/', views.playlist, name='playlist'),  # Playlist view
    path('movie/<int:movie_id>/', views.movie_details_page, name='movie-details'),
    path('search/', views.search_movies, name='search-movies'),
]
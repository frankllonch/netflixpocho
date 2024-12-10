from django.urls import path
from . import views

urlpatterns = [
    path("", views.start, name="start"),  # Start view
    path("home/", views.home, name="home"),  # Home view
    path("series/", views.home_series, name="series"),
    path("playlist/", views.playlist, name="playlist"),  # Playlist view
    path("movie/<int:movie_id>/", views.movie_details_page, name="movie-details"),
    path("search/", views.search_movies, name="search-movies"),
    path("add-to-playlist-movies/<int:movie_id>/",views.add_to_playlist_movie,name="add-to-playlist-movies"),
    path("add-to-playlist-series/<int:series_id>/",views.add_to_playlist_series,name="add-to-playlist-series"),
]

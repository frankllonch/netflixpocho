from django.shortcuts import get_object_or_404, redirect
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Movie, Playlist, Recommendation
from .serializers import MovieSerializer, PlaylistSerializer, RecommendationSerializer
from django.shortcuts import render
from .models import Movie, Playlist, Series
import requests
import random
from django.conf import settings
from django.shortcuts import render
from django.db.models import Q  # For complex queries
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required


def validate_date(date_str):
    try:
        # Try to parse the date in YYYY-MM-DD format
        return datetime.strptime(date_str, "%Y-%m-%d").date()
    except (ValueError, TypeError):
        # Return None if the date is invalid or empty
        return None


# Function-based views
def movie_details(request, movie_id):
    movie = get_object_or_404(Movie, id=movie_id)
    serializer = MovieSerializer(movie)
    return Response(serializer.data)


def movie_details_page(request, movie_id):
    try:
        movie = get_object_or_404(Movie, id=movie_id)
        print(f"Loaded movie: {movie.title}")
    except Exception as e:
        print(f"Error loading movie: {e}")
    return render(request, "streaming/movie_details.html", {"movie": movie})


def popular_movies(request):
    # Dummy implementation, replace with actual logic
    movies = Movie.objects.filter(rating__gte=8.0)[:10000]
    serializer = MovieSerializer(movies, many=True)
    return Response(serializer.data)


# Class-based views
class RecommendationView(APIView):
    def get(self, request, movie_id):
        recommendation = get_object_or_404(Recommendation, movie_id=movie_id)
        serializer = RecommendationSerializer(recommendation)
        return Response(serializer.data)


class MovieListView(APIView):
    def get(self, request):
        movies = Movie.objects.all()
        serializer = MovieSerializer(movies, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = MovieSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class MovieDetailView(APIView):
    def get(self, request, movie_id):
        movie = get_object_or_404(Movie, id=movie_id)
        serializer = MovieSerializer(movie)
        return Response(serializer.data)


def populate_movies():
    """
    Fetch and save the top 10000 popular movies from TMDB to the database.
    """
    for page in range(
        1, 20
    ):  # Fetch up to 5 pages of movies (20 movies per page = 1000 movies)
        api_url = "https://api.themoviedb.org/3/movie/popular"
        params = {
            "api_key": settings.TMDB_API_KEY,
            "language": "en-US",
            "page": page,
        }
        response = requests.get(api_url, params=params)
        if response.status_code == 200:
            popular_movies = response.json().get("results", [])
            for movie in popular_movies:
                # Avoid duplicates by using get_or_create
                Movie.objects.get_or_create(
                    id=movie["id"],
                    defaults={
                        "title": movie.get("title", "Unknown Title"),
                        "description": movie.get(
                            "overview", "No description available."
                        ),
                        "release_date": validate_date(
                            movie.get("first_air_date", "")
                        ),  # Validate the date
                        "genre": (
                            ", ".join(
                                [genre["name"] for genre in movie.get("genres", [])]
                            )
                            if "genres" in movie
                            else "Unknown"
                        ),
                        "rating": movie.get("vote_average", 0),
                        "poster_path": movie.get("poster_path", ""),
                    },
                )
        else:
            print(f"Failed to fetch page {page}. Status code: {response.status_code}")

@login_required
def home(request):
    # Populate the database if it's empty
    if Movie.objects.count() < 1000:  # Ensure at least 1000 movies are in the database
        populate_movies()

    # Fetch the top movies sorted by rating
    movies = Movie.objects.all().order_by("-rating")[:1000]

    # Get or create the user's playlist
    playlist, _ = Playlist.objects.get_or_create(user=request.user, name="My Playlist")
    playlist_movie_ids = list(playlist.movies.values_list("id", flat=True))

    # Render the template with movies and playlist data
    return render(
        request,
        "streaming/home.html",
        {
            "movies": movies,
            "playlists": playlist_movie_ids,  # Pass list of favorited movie IDs
        },
    )


@login_required
def playlist(request):
    playlist, _ = Playlist.objects.get_or_create(user=request.user)
    return render(request, "streaming/playlist.html", {"playlists": playlist})


def movie_details_page(request, movie_id):
    # Fetch the movie from the database
    movie = get_object_or_404(Movie, id=movie_id)
    return render(request, "streaming/movie_details.html", {"movie": movie})


def search_movies(request):
    query = request.GET.get("q", "")
    category = request.GET.get("category", "movie")  # Default to movies
    genre_id = request.GET.get("genre", None)  # Get selected genre ID
    movies = []
    series = []
    genres = []

    if query:
        # TMDB API calls to search movies
        movie_api_url = "https://api.themoviedb.org/3/search/movie"
        movie_params = {
            "api_key": settings.TMDB_API_KEY,
            "language": "en-US",
            "query": query,
            "page": 1,
            "include_adult": False,
        }
        movie_response = requests.get(movie_api_url, movie_params)
        if movie_response.status_code == 200:
            movies = movie_response.json().get("results", [])

        # TMDB API call to search series
        series_api_url = "https://api.themoviedb.org/3/search/tv"
        series_params = {
            "api_key": settings.TMDB_API_KEY,
            "language": "en-US",
            "query": query,
            "page": 1,
        }
        series_response = requests.get(series_api_url, series_params)
        if series_response.status_code == 200:
            series = series_response.json().get("results", [])

    # TMDB API call to get genres
    genre_api_url = f"https://api.themoviedb.org/3/genre/{category}/list"
    genre_params = {
        "api_key": settings.TMDB_API_KEY,
        "language": "en-US",
    }
    genre_response = requests.get(genre_api_url, genre_params)
    if genre_response.status_code == 200:
        genres = genre_response.json().get("genres", [])

    # Fetch IDs of movies and series in the user's playlist
    playlist = Playlist.objects.first()  # Assuming a single playlist
    playlist_movie_ids = playlist.movies.values_list("id", flat=True) if playlist else []
    playlist_series_ids = playlist.series.values_list("id", flat=True) if playlist else []

    return render(
        request,
        "streaming/search_results.html",
        {
            "movies": movies,
            "series": series,
            "query": query,
            "category": category,
            "genres": genres,
            "selected_genre": genre_id,
            "playlist_movie_ids": playlist_movie_ids,
            "playlist_series_ids": playlist_series_ids,
        },
    )
    

@login_required
def add_to_playlist_movie(request, movie_id):
    if request.method == "POST":
        # Get or create the user's playlist
        playlist, _ = Playlist.objects.get_or_create(user=request.user, name="My Playlist")

        try:
            # Check if the movie exists in the database
            movie = Movie.objects.get(id=movie_id)
        except Movie.DoesNotExist:
            # Fetch movie details from TMDB API
            api_url = f"https://api.themoviedb.org/3/movie/{movie_id}"
            params = {"api_key": settings.TMDB_API_KEY, "language": "en-US"}
            response = requests.get(api_url, params=params)

            if response.status_code == 200:
                data = response.json()
                # Save the movie in the database
                movie = Movie.objects.create(
                    id=movie_id,
                    title=data.get("title", "Unknown Title"),
                    description=data.get("overview", ""),
                    release_date=data.get("release_date", None),
                    genre=", ".join([genre["name"] for genre in data.get("genres", [])]),
                    rating=data.get("vote_average", 0),
                    poster_path=data.get("poster_path", ""),
                )
            else:
                return redirect("home")  # Handle API failure

        # Toggle the movie in the playlist
        if movie in playlist.movies.all():
            playlist.movies.remove(movie)  # Remove from playlist
        else:
            playlist.movies.add(movie)  # Add to playlist

        # Redirect back to the referring page
        return redirect(request.META.get('HTTP_REFERER', 'playlist'))

    return redirect("home")  # Fallback redirect


from django.shortcuts import render
from datetime import datetime


def start(request):
    """
    Render the start page with navigation links.
    """
    return render(request, "streaming/start.html")


def populate_series():
    """
    Fetch and save the top 1000 popular TV series from TMDB to the database.
    """
    for page in range(
        1, 15
    ):  # Fetch up to 5 pages of TV series (20 per page = 1000 series)
        api_url = "https://api.themoviedb.org/3/tv/popular"
        params = {
            "api_key": settings.TMDB_API_KEY,
            "language": "en-US",
            "page": page,
        }
        response = requests.get(api_url, params=params)
        if response.status_code == 200:
            popular_series = response.json().get("results", [])
            for series in popular_series:
                # Avoid duplicates by using get_or_create
                Series.objects.get_or_create(
                    id=series["id"],
                    defaults={
                        "title": series.get("name", "Unknown Title"),
                        "description": series.get(
                            "overview", "No description available."
                        ),
                        "release_date": validate_date(series.get("first_air_date")),
                        "genre": (
                            ", ".join(
                                [
                                    str(genre_id)
                                    for genre_id in series.get("genre_ids", [])
                                ]
                            )
                            if "genre_ids" in series
                            else "Unknown"
                        ),
                        "rating": series.get("vote_average", 0),
                        "poster_path": series.get("poster_path", ""),
                    },
                )
        else:
            print(f"Failed to fetch page {page}. Status code: {response.status_code}")

@login_required
def home_series(request):
    # Populate the series database if it's empty
    if Series.objects.count() < 1000:  # Ensure at least 1000 series are in the database
        populate_series()

    # Fetch the top series sorted by rating
    series_list = Series.objects.all().order_by("-rating")[:1000]

    # Get or create the user's playlist
    playlist, _ = Playlist.objects.get_or_create(user=request.user, name="My Playlist")
    playlist_series_ids = list(playlist.series.values_list("id", flat=True))

    # Render the template with series and playlist data
    return render(
        request,
        "streaming/home_series.html",
        {
            "series_list": series_list,
            "playlists": playlist_series_ids,  # Pass list of favorited series IDs
        },
    )

@login_required
def add_to_playlist_series(request, series_id):
    if request.method == "POST":
        # Get or create the user's playlist
        playlist, _ = Playlist.objects.get_or_create(user=request.user, name="My Playlist")

        try:
            # Check if the series exists in the database
            series = Series.objects.get(id=series_id)
        except Series.DoesNotExist:
            # Fetch series details from TMDB API
            api_url = f"https://api.themoviedb.org/3/tv/{series_id}"
            params = {"api_key": settings.TMDB_API_KEY, "language": "en-US"}
            response = requests.get(api_url, params=params)

            if response.status_code == 200:
                data = response.json()
                # Save the series in the database
                series = Series.objects.create(
                    id=series_id,
                    title=data.get("name", "Unknown Title"),
                    description=data.get("overview", ""),
                    release_date=data.get("first_air_date", None),
                    genre=", ".join([genre["name"] for genre in data.get("genres", [])]),
                    rating=data.get("vote_average", 0),
                    poster_path=data.get("poster_path", ""),
                )
            else:
                return redirect("series")  # Handle API failure

        # Toggle the series in the playlist
        if series in playlist.series.all():
            playlist.series.remove(series)  # Remove from playlist
        else:
            playlist.series.add(series)  # Add to playlist

        # Redirect back to the referring page
        return redirect(request.META.get('HTTP_REFERER', 'playlist'))

    return redirect("series")  # Fallback redirect
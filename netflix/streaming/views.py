from django.shortcuts import get_object_or_404, redirect
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Movie, Playlist, Recommendation
from .serializers import MovieSerializer, PlaylistSerializer, RecommendationSerializer
from django.shortcuts import render
from .models import Movie, Playlist
import requests
import random
from django.conf import settings
from django.shortcuts import render
from django.db.models import Q  # For complex queries
from django.core.paginator import Paginator


# Function-based views
def movie_details(request, movie_id):
    movie = get_object_or_404(Movie, id=movie_id)
    serializer = MovieSerializer(movie)
    return Response(serializer.data)


def popular_movies(request):
    # Dummy implementation, replace with actual logic
    movies = Movie.objects.filter(rating__gte=8.0)[:100]
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


def home(request):
    # Populate the database if it's empty
    if Movie.objects.count() < 100:  # Ensure at least 100 movies are in the database
        populate_movies()

    # Fetch the top 100 movies sorted by rating
    movies = Movie.objects.all().order_by('-rating')[:100]

    # Fetch IDs of movies in the user's playlist
    playlist, _ = Playlist.objects.get_or_create(name="My Playlist")
    playlist_movie_ids = list(playlist.movies.values_list("id", flat=True))

    # Render the template with all movies and playlist movie IDs
    return render(request, 'streaming/home.html', {
        'movies': movies,
        'playlists': playlist_movie_ids,  # Pass list of favorited movie IDs
    })

def playlist(request):
    playlist, _ = Playlist.objects.get_or_create(name="My Playlist")
    return render(request, 'streaming/playlist.html', {'playlists': playlist})

def movie_details_page(request, movie_id):
    # Fetch the movie from the database
    movie = get_object_or_404(Movie, id=movie_id)
    return render(request, "streaming/movie_details.html", {"movie": movie})


def search_movies(request):
    query = request.GET.get('q', '')  # Get the search term from the request
    movies = []
    if query:
        # TMDB API call to search movies
        api_url = "https://api.themoviedb.org/3/search/movie"
        params = {
            'api_key': settings.TMDB_API_KEY,
            'language': 'en-US',
            'query': query,
            'page': 1,  # Change this for pagination if needed
            'include_adult': False
        }
        response = requests.get(api_url, params=params)
        if response.status_code == 200:
            movies = response.json().get('results', [])  # Extract results from the API

    # Pass the movies and the query back to the template
    return render(request, 'streaming/search_results.html', {
        'movies': movies,
        'query': query
    })

def add_to_playlist(request, movie_id):
    if request.method == 'POST':
        # Get or create the default playlist
        playlist, _ = Playlist.objects.get_or_create(name='My Playlist')

        try:
            # Check if the movie exists in the database
            movie = Movie.objects.get(id=movie_id)
        except Movie.DoesNotExist:
            # Fetch movie details from TMDB API
            api_url = f"https://api.themoviedb.org/3/movie/{movie_id}"
            params = {'api_key': settings.TMDB_API_KEY, 'language': 'en-US'}
            response = requests.get(api_url, params=params)

            if response.status_code == 200:
                data = response.json()
                # Save the movie in the database
                movie = Movie.objects.create(
                    id=movie_id,
                    title=data['title'],
                    description=data['overview'],
                    release_date=data['release_date'],
                    genre=', '.join([genre['name'] for genre in data['genres']]),
                    rating=data['vote_average'],
                    poster_path=data['poster_path'],
                )
            else:
                return redirect('home')  # Handle API failure

        # Toggle the movie in the playlist
        if movie in playlist.movies.all():
            playlist.movies.remove(movie)  # Remove from playlist
        else:
            playlist.movies.add(movie)  # Add to playlist

    return redirect('home')  # Redirect back to home


def populate_series():
    """
    Fetch and save the top 100 popular TV series from TMDB to the database.
    """
    for page in range(1, 6):  # Fetch up to 5 pages of TV series (20 per page = 100 series)
        api_url = "https://api.themoviedb.org/3/tv/popular"
        params = {
            'api_key': settings.TMDB_API_KEY,
            'language': 'en-US',
            'page': page,
        }
        response = requests.get(api_url, params=params)
        if response.status_code == 200:
            popular_series = response.json().get('results', [])
            for series in popular_series:
                # Default to an empty string if poster_path is missing
                poster_path = series.get('poster_path', '')
                Movie.objects.get_or_create(
                    id=series['id'],
                    defaults={
                        'title': series.get('name', 'Unknown Title'),
                        'description': series.get('overview', 'No description available.'),
                        'release_date': series.get('first_air_date', 'Unknown Date'),
                        'genre': ', '.join([genre['name'] for genre in series.get('genres', [])]) if 'genres' in series else 'Unknown',
                        'rating': series.get('vote_average', 0),
                        'poster_path': poster_path or '/default-poster.png',  # Provide a default poster path
                    },
                )
        else:
            print(f"Failed to fetch page {page}. Status code: {response.status_code}")

def start(request):
    return render(request, 'streaming/start.html')

def populate_series():
    """
    Fetch and save the top 100 popular TV series from TMDB to the database.
    """
    for page in range(1, 6):  # Fetch up to 5 pages of TV series (20 per page = 100 series)
        api_url = "https://api.themoviedb.org/3/tv/popular"
        params = {
            'api_key': settings.TMDB_API_KEY,
            'language': 'en-US',
            'page': page,
        }
        response = requests.get(api_url, params=params)
        if response.status_code == 200:
            popular_series = response.json().get('results', [])
            for series in popular_series:
                # Avoid duplicates by using get_or_create
                Movie.objects.get_or_create(
                    id=series['id'],
                    defaults={
                        'title': series.get('name', 'Unknown Title'),  # `name` is used for series
                        'description': series.get('overview', 'No description available.'),
                        'release_date': series.get('first_air_date', 'Unknown Date'),
                        'genre': ', '.join([genre['name'] for genre in series.get('genres', [])]) if 'genres' in series else 'Unknown',
                        'rating': series.get('vote_average', 0),
                        'poster_path': series.get('poster_path', ''),
                    },
                )
        else:
            print(f"Failed to fetch page {page}. Status code: {response.status_code}")

def home_series(request):
    """
    Display the top 100 popular series from the database.
    """
    # Populate the database if it's empty
    if Movie.objects.count() < 100:  # Ensure at least 100 series are in the database
        populate_series()

    # Fetch the top 100 series sorted by rating
    series = Movie.objects.all().order_by('-rating')[:100]

    # Fetch IDs of series in the user's playlist
    playlist, _ = Playlist.objects.get_or_create(name="My Playlist")
    playlist_series_ids = list(playlist.movies.values_list("id", flat=True))

    # Render the template with all series and playlist series IDs
    return render(request, 'streaming/home_series.html', {
        'movies': series,  # Reusing the 'movies' variable for series
        'playlists': playlist_series_ids,  # Pass list of favorited series IDs
    })
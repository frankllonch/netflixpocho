from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Movie, Playlist, Recommendation
from .serializers import MovieSerializer, PlaylistSerializer, RecommendationSerializer
from django.shortcuts import render
from .models import Movie



# Function-based views
def movie_details(request, movie_id):
    movie = get_object_or_404(Movie, id=movie_id)
    serializer = MovieSerializer(movie)
    return Response(serializer.data)


def popular_movies(request):
    # Dummy implementation, replace with actual logic
    movies = Movie.objects.filter(rating__gte=8.0)[:10]
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


import requests
import random
from django.conf import settings
from django.shortcuts import render

def home(request):
    # TMDB API call to fetch popular movies
    api_url = "https://api.themoviedb.org/3/movie/popular"
    params = {
        'api_key': settings.TMDB_API_KEY,  # Ensure your TMDB_API_KEY is in settings
        'language': 'en-US',
        'page': 1
    }
    response = requests.get(api_url, params=params)
    if response.status_code == 200:
        popular_movies = response.json().get('results', [])
        # Select a random subset of movies (e.g., 10 movies)
        movies = random.sample(popular_movies, min(len(popular_movies), 10))
    else:
        movies = []  # Handle API failure gracefully

    return render(request, 'streaming/home.html', {'movies': movies})

def playlist(request):
    return render(request, "streaming/playlist.html")  # Render the playlist template


def movie_details_page(request, movie_id):
    # Fetch the movie from the database
    movie = get_object_or_404(Movie, id=movie_id)
    return render(request, "streaming/movie_details.html", {"movie": movie})


from django.db.models import Q  # For complex queries


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
            'page': 1,
            'include_adult': False
        }
        response = requests.get(api_url, params=params)
        if response.status_code == 200:
            movies = response.json().get('results', [])

    return render(request, 'streaming/search_results.html', {'movies': movies, 'query': query})
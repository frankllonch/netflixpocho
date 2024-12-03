import requests
from django.conf import settings

def fetch_movie_data(movie_id):
    try:
        api_url = f"https://api.themoviedb.org/3/movie/{movie_id}"
        params = {'api_key': settings.TMDB_API_KEY}
        response = requests.get(api_url, params=params)
        response.raise_for_status()  # Raise an error for bad status codes
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}
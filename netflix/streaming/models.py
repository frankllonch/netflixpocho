from django.db import models
from django.contrib.auth.models import User
from django import forms

class Movie(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    release_date = models.DateField(blank=True, null=True)
    genre = models.TextField(max_length=100, blank=True, null=True)
    rating = models.FloatField(blank=True, null=True)
    poster_path = models.URLField(blank=True, null=True)

    def __str__(self):
        return self.title

class Series(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    release_date = models.DateField(blank=True, null=True)
    genre = models.TextField(max_length=100, blank=True, null=True)
    rating = models.FloatField(blank=True, null=True)
    poster_path = models.URLField(blank=True, null=True)  # Allow NULL values

    def __str__(self):
        return self.title


from django.db import models
from django.contrib.auth.models import User

class Playlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="playlists")
    name = models.CharField(max_length=100, default="My Playlist")
    movies = models.ManyToManyField("Movie", related_name="playlists", blank=True)
    series = models.ManyToManyField("Series", related_name="playlists", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}'s Playlist"


class Recommendation(models.Model):
    movie = models.OneToOneField(Movie, on_delete=models.CASCADE)
    recommended_movies = models.ManyToManyField(Movie, related_name="recommendations")

    def __str__(self):
        return f"Recommendations for {self.movie.title}"



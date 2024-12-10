from django.db import models


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


class Playlist(models.Model):
    name = models.CharField(max_length=100)
    movies = models.ManyToManyField(Movie, related_name="playlists")
    created_at = models.DateTimeField(auto_now_add=True)
    series = models.ManyToManyField(Series, related_name="playlists")

    def __str__(self):
        return self.name


class Recommendation(models.Model):
    movie = models.OneToOneField(Movie, on_delete=models.CASCADE)
    recommended_movies = models.ManyToManyField(Movie, related_name="recommendations")

    def __str__(self):
        return f"Recommendations for {self.movie.title}"



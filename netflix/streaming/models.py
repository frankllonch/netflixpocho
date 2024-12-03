from django.db import models

class Movie(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    release_date = models.DateField()
    genre = models.CharField(max_length=100)
    rating = models.FloatField()
    poster_path = models.URLField()

    def __str__(self):
        return self.title

class Playlist(models.Model):
    name = models.CharField(max_length=100)
    movies = models.ManyToManyField(Movie, related_name="playlists")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Recommendation(models.Model):
    movie = models.OneToOneField(Movie, on_delete=models.CASCADE)
    recommended_movies = models.ManyToManyField(Movie, related_name="recommendations")

    def __str__(self):
        return f"Recommendations for {self.movie.title}"
from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify


class Genre(models.Model):
    """Musical genre model with Spotify integration support."""
    name = models.CharField(max_length=100, unique=True)
    spotify_id = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Artist(models.Model):
    """Artist model with genre relationships and Spotify integration."""
    name = models.CharField(max_length=200)
    spotify_id = models.CharField(max_length=50, blank=True, null=True)
    spotify_url = models.URLField(blank=True, null=True)
    genres = models.ManyToManyField(Genre, blank=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Song(models.Model):
    """Song model with artist relationship and Spotify metadata."""
    title = models.CharField(max_length=200)
    artist = models.ForeignKey(
        Artist, on_delete=models.CASCADE, related_name='songs')
    spotify_id = models.CharField(max_length=50, blank=True, null=True)
    spotify_url = models.URLField(blank=True, null=True)
    album_name = models.CharField(max_length=200, blank=True, null=True)
    duration_ms = models.IntegerField(
        blank=True, null=True, help_text="Duration in milliseconds")
    key = models.CharField(max_length=10, blank=True,
                           null=True, help_text="Musical key (e.g., C, Am, F#)")
    tempo_bpm = models.IntegerField(
        blank=True, null=True, help_text="Tempo in beats per minute")
    created_by = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='created_songs')
    genres = models.ManyToManyField(Genre, blank=True)
    slug = models.SlugField(unique=True, max_length=250)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['title', 'artist__name']
        unique_together = ('title', 'artist')

    def save(self, *args, **kwargs):
        """Generate slug from title and artist name if not provided."""
        if not self.slug:
            base_slug = slugify(f"{self.title} {self.artist.name}")
            slug = base_slug
            counter = 1
            while Song.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.title} - {self.artist.name}"

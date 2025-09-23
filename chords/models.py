from django.db import models
from django.contrib.auth.models import User
from music.models import Song


class Tag(models.Model):
    """Tag model for categorizing chord sheets."""
    name = models.CharField(max_length=50, unique=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class ChordSheet(models.Model):
    """User-generated chord sheet model with song relationship."""
    song = models.ForeignKey(
        Song, on_delete=models.CASCADE, related_name='chord_sheets')
    content = models.TextField(
        help_text="Chord sheet content with chords and lyrics")
    capo = models.IntegerField(
        default=0, help_text="Capo position (0 = no capo)")
    transposition = models.IntegerField(
        default=0, help_text="Transposition in semitones (+/- 12)")
    created_by = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='chord_sheets')
    is_public = models.BooleanField(
        default=True, help_text="Whether this chord sheet is publicly visible")
    tags = models.ManyToManyField(Tag, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        visibility = "Public" if self.is_public else "Private"
        return f"{self.song.title} - {self.created_by.username} ({visibility})"


class Favorite(models.Model):
    """User favorites model for tracking favorite songs."""
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='favorites')
    song = models.ForeignKey(
        Song, on_delete=models.CASCADE, related_name='favorited_by')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'song')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.song.title}"

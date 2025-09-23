from django.test import TestCase
from django.contrib.auth.models import User
from .models import Genre, Artist, Song


class MusicModelsTestCase(TestCase):
    """Test cases for music app models."""

    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.genre = Genre.objects.create(name='Rock')
        self.artist = Artist.objects.create(name='Test Artist')
        self.artist.genres.add(self.genre)

    def test_genre_creation(self):
        """Test Genre model creation and string representation."""
        self.assertEqual(str(self.genre), 'Rock')
        self.assertEqual(self.genre.name, 'Rock')

    def test_artist_creation(self):
        """Test Artist model creation and relationships."""
        self.assertEqual(str(self.artist), 'Test Artist')
        self.assertEqual(self.artist.name, 'Test Artist')
        self.assertIn(self.genre, self.artist.genres.all())

    def test_song_creation_and_slug_generation(self):
        """Test Song model creation and automatic slug generation."""
        song = Song.objects.create(
            title='Test Song',
            artist=self.artist,
            created_by=self.user
        )
        self.assertEqual(str(song), 'Test Song - Test Artist')
        self.assertEqual(song.slug, 'test-song-test-artist')

    def test_song_unique_slug_generation(self):
        """Test that songs with similar titles get unique slugs."""
        # Create another artist to avoid unique_together constraint
        artist2 = Artist.objects.create(name='Test Artist')

        song1 = Song.objects.create(
            title='Test Song',
            artist=self.artist,
            created_by=self.user
        )
        song2 = Song.objects.create(
            title='Test Song',
            artist=artist2,
            created_by=self.user
        )
        self.assertEqual(song1.slug, 'test-song-test-artist')
        self.assertEqual(song2.slug, 'test-song-test-artist-1')

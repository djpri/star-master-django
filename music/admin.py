from django.contrib import admin
from .models import Genre, Artist, Song


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    """Admin interface for Genre model."""
    list_display = ('name', 'spotify_id')
    search_fields = ('name',)
    ordering = ('name',)


@admin.register(Artist)
class ArtistAdmin(admin.ModelAdmin):
    """Admin interface for Artist model."""
    list_display = ('name', 'spotify_id', 'get_genres_display')
    search_fields = ('name',)
    list_filter = ('genres',)
    filter_horizontal = ('genres',)
    ordering = ('name',)

    def get_genres_display(self, obj):
        """Display genres as comma-separated list."""
        return ", ".join([genre.name for genre in obj.genres.all()[:3]])
    get_genres_display.short_description = 'Genres'


@admin.register(Song)
class SongAdmin(admin.ModelAdmin):
    """Admin interface for Song model."""
    list_display = ('title', 'artist', 'album_name', 'key',
                    'tempo_bpm', 'created_by', 'created_at')
    search_fields = ('title', 'artist__name', 'album_name')
    list_filter = ('genres', 'artist', 'created_by', 'created_at')
    filter_horizontal = ('genres',)
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('title', 'artist__name')

    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'artist', 'album_name', 'slug')
        }),
        ('Musical Details', {
            'fields': ('key', 'tempo_bpm', 'duration_ms', 'genres')
        }),
        ('Spotify Integration', {
            'fields': ('spotify_id', 'spotify_url'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )

from django.contrib import admin
from .models import ChordSheet, Tag, Favorite


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """Admin interface for Tag model."""
    list_display = ('name',)
    search_fields = ('name',)
    ordering = ('name',)


@admin.register(ChordSheet)
class ChordSheetAdmin(admin.ModelAdmin):
    """Admin interface for ChordSheet model."""
    list_display = ('song', 'created_by', 'is_public',
                    'capo', 'transposition', 'created_at')
    list_filter = ('is_public', 'capo', 'created_at', 'tags')
    search_fields = ('song__title', 'song__artist__name',
                     'created_by__username', 'content')
    filter_horizontal = ('tags',)
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Song Information', {
            'fields': ('song', 'created_by')
        }),
        ('Chord Sheet Content', {
            'fields': ('content', 'capo', 'transposition', 'is_public')
        }),
        ('Categorization', {
            'fields': ('tags',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    """Admin interface for Favorite model."""
    list_display = ('user', 'song', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__username', 'song__title', 'song__artist__name')
    readonly_fields = ('created_at',)

from django.contrib import admin
from .models import Tag, Question, QuestionVote


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('title', 'owner', 'status', 'is_public', 'created_at')
    list_filter = ('status', 'is_public', 'created_at', 'tags')
    search_fields = ('title', 'body')
    filter_horizontal = ('tags',)
    readonly_fields = ('created_at', 'updated_at', 'search_vector')


@admin.register(QuestionVote)
class QuestionVoteAdmin(admin.ModelAdmin):
    list_display = ('user', 'question', 'rating', 'created_at')
    list_filter = ('rating', 'created_at')
    readonly_fields = ('created_at',)

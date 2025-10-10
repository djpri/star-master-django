from django.contrib import admin
from .models import Tag, Question, QuestionVote


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "is_public", "owner", "created_at")
    list_filter = ("is_public", "created_at")
    search_fields = ("name", "owner__username")
    prepopulated_fields = {"slug": ("name",)}
    readonly_fields = ("created_at",)


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ("title", "owner", "status", "is_public", "created_at")
    list_filter = ("status", "is_public", "created_at", "tags")
    search_fields = ("title", "body")
    filter_horizontal = ("tags",)
    readonly_fields = ("created_at", "updated_at", "search_vector")


@admin.register(QuestionVote)
class QuestionVoteAdmin(admin.ModelAdmin):
    list_display = ("user", "question", "rating", "created_at")
    list_filter = ("rating", "created_at")
    readonly_fields = ("created_at",)

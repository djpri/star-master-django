from django.contrib import admin
from .models import Answer, StarAnswer, BasicAnswer


@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ('user', 'question', 'answer_type',
                    'is_public', 'created_at')
    list_filter = ('answer_type', 'is_public', 'created_at')
    search_fields = ('question__title',)
    readonly_fields = ('created_at', 'updated_at', 'search_vector')


@admin.register(StarAnswer)
class StarAnswerAdmin(admin.ModelAdmin):
    list_display = ('user', 'question', 'is_public', 'created_at')
    list_filter = ('is_public', 'created_at')
    search_fields = ('question__title', 'situation',
                     'task', 'action', 'result')
    readonly_fields = ('created_at', 'updated_at', 'search_vector')
    fieldsets = (
        (None, {
            'fields': ('question', 'user', 'is_public')
        }),
        ('STAR Content', {
            'fields': ('situation', 'task', 'action', 'result')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(BasicAnswer)
class BasicAnswerAdmin(admin.ModelAdmin):
    list_display = ('user', 'question', 'is_public', 'created_at')
    list_filter = ('is_public', 'created_at')
    search_fields = ('question__title', 'text')
    readonly_fields = ('created_at', 'updated_at', 'search_vector')

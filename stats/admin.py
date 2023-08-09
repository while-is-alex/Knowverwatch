from django.contrib import admin
from .models import Team, Player, Segment, Match


class TeamAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'code',
        'region',
    )
    list_filter = (
        'region',
    )
    prepopulated_fields = {
        'slug': (
            'name',
        )
    }


class PlayerAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'role',
        'team',
    )
    list_filter = (
        'team',
        'role',
    )
    prepopulated_fields = {
        'slug': (
            'name',
        )
    }


class SegmentAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'season',
    )
    list_filter = (
        'season',
    )
    prepopulated_fields = {
        'slug': (
            'name',
        )
    }


class MatchAdmin(admin.ModelAdmin):
    list_display = (
        'teams',
        'segment',
        'season',
    )
    list_filter = (
        'segment',
        'season',
    )
    prepopulated_fields = {
        'slug': (
            'id',
        )
    }


admin.site.register(Team, TeamAdmin)
admin.site.register(Player, PlayerAdmin)
admin.site.register(Segment, SegmentAdmin)
admin.site.register(Match, MatchAdmin)

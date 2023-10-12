from django.contrib import admin
from .models import Team, Player, Segment, Match, Award


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
        'id',
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


class AwardAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'year',
        'team',
        'player',
    )
    list_filter = (
        'name',
        'year',
    )
    prepopulated_fields = {
        'slug': (
            'name',
        )
    }


admin.site.register(Team, TeamAdmin)
admin.site.register(Player, PlayerAdmin)
admin.site.register(Segment, SegmentAdmin)
admin.site.register(Match, MatchAdmin)
admin.site.register(Award, AwardAdmin)

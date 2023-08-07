from django.contrib import admin
from .models import Team, Player, Segment, Match


class TeamAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'code',
    )
    prepopulated_fields = {
        'slug': (
            'name',
        )
    }


class PlayerAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'team',
    )
    prepopulated_fields = {
        'slug': (
            'name',
        )
    }
    list_filter = (
        'team',
    )


class SegmentAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'season',
    )
    prepopulated_fields = {
        'slug': (
            'name',
        )
    }
    list_filter = (
        'season',
    )


class MatchAdmin(admin.ModelAdmin):
    list_display = (
        'teams',
        'segment',
        'season',
    )
    prepopulated_fields = {
        'slug': (
            'id',
        )
    }
    list_filter = (
        'segment',
        'season',
    )


admin.site.register(Team, TeamAdmin)
admin.site.register(Player, PlayerAdmin)
admin.site.register(Segment, SegmentAdmin)
admin.site.register(Match, MatchAdmin)

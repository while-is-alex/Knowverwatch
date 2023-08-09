from OWLAPI import Owl
from django.shortcuts import render
from django.views import View
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.core.paginator import Paginator
from .models import Team, Player, Segment, Match

owl = Owl()


class HomeView(View):
    def get(self, request):

        return render(
            request,
            'stats/index.html',
        )


class TeamsView(View):
    def get(self, request):
        all_teams = Team.objects.all().order_by('name')

        return render(
            request,
            'stats/teams.html',
            {
                'teams': all_teams,
            }
        )


class TeamDetailsView(View):
    def get(self, request, slug):
        selected_team = Team.objects.get(slug=slug)
        roster = []
        for player in selected_team.players.all().order_by('role'):
            roster.append(player)

        return render(
            request,
            'stats/team-details.html',
            {
                'team': selected_team,
                'players': roster,
            }
        )


class PlayersView(View):
    def get(self, request):
        all_players = Player.objects.all().order_by('name')

        paginator = Paginator(all_players, 20)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        return render(
            request,
            'stats/players.html',
            {
                'page_obj': page_obj,
                'request': request,
            }
        )


class PlayerDetailsView(View):
    def get(self, request, slug):
        selected_player = Player.objects.get(slug=slug)

        if selected_player is None:

            return HttpResponseRedirect(
                reverse(
                    'home-page',
                )
            )

        return render(
            request,
            'stats/player-details.html',
            {
                'player': selected_player,
            }
        )


class SearchView(View):
    def get(self, request):
        search = request.GET['search']

        all_players = Player.objects.all()
        player_found = None
        for player in all_players:
            if search.lower() in player.name.lower().split():
                player_found = player

        if player_found is not None:

            return HttpResponseRedirect(
                reverse(
                    'player-details-page',
                    args=[player_found.slug]
                )
            )

        all_teams = Team.objects.all()
        team_found = None
        for team in all_teams:
            if search.lower() in team.name.lower().split():
                team_found = team

        if team_found is not None:

            return HttpResponseRedirect(
                reverse(
                    'team-details-page',
                    args=[team_found.slug]
                )
            )

        return render(
            request,
            'stats/index.html',
        )
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
        all_teams = owl.get_all_teams()

        return render(
            request,
            'stats/teams.html',
            {
                'teams': all_teams,
                'request': request,
            }
        )


class TeamDetailsView(View):
    def get(self, request, team_id):
        selected_team = owl.get_team(team_id)

        roster = []
        for player in selected_team['roster']:
            current_player = owl.get_player(player)
            roster.append(current_player)

        return render(
            request,
            'stats/team-details.html',
            {
                'team': selected_team,
                'players': roster,
                'request': request,
            }
        )


class PlayersView(View):
    def get(self, request):
        all_teams = owl.get_all_teams()
        all_players = owl.get_all_players()

        paginator = Paginator(all_players, 20)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        return render(
            request,
            'stats/players.html',
            {
                'page_obj': page_obj,
                'request': request,
                'teams': all_teams,
            }
        )


class PlayerDetailsView(View):
    def get(self, request, player_id):
        selected_player = owl.get_player(player_id)
        team = owl.get_team(selected_player['teams'][-1]['id'])

        if team is None:
            team = owl.get_team(selected_player['teams'][0]['id'])

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
                'team': team,
                'request': request,
            }
        )


class SearchView(View):
    def get(self, request):
        search = request.GET['search']

        player_id = owl.get_player_id(search)
        team_id = owl.get_team_id(search)

        if player_id is not None:

            return HttpResponseRedirect(
                reverse(
                    'player-details-page',
                    args=[player_id],
                )
            )

        if team_id is not None:

            return HttpResponseRedirect(
                reverse(
                    'team-details-page',
                    args=[team_id],
                )
            )

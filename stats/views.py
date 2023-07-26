from OWLAPI import Owl
from django.shortcuts import render
from django.views import View
from django.http import HttpResponseRedirect
from django.urls import reverse


class HomeView(View):
    def get(self, request):
        return render(
            request,
            'stats/index.html',
            {

            }
        )


class TeamsView(View):
    def get(self, request):
        owl = Owl()
        all_teams = owl.all_teams()

        return render(
            request,
            'stats/teams.html',
            {
                'teams': all_teams,
            }
        )


class TeamDetailsView(View):
    def get(self, request, team_id):
        owl = Owl()
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
            }
        )


class PlayersView(View):
    def get(self, request):
        owl = Owl()
        all_players = owl.all_players()

        return render(
            request,
            'stats/players.html',
            {
                'players': all_players,
            }
        )


class PlayerDetailsView(View):
    def get(self, request, player_id):
        owl = Owl()
        selected_player = owl.get_player(player_id)

        if selected_player == 'Not found':
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
        owl = Owl()
        search = request.GET['search']
        team_id = owl.get_team_id(search)
        player_id = owl.get_player_id(search)

        if team_id != 'Not found':
            print('team not found')

            return HttpResponseRedirect(
                reverse(
                    'team-details-page',
                    args=[team_id],
                )
            )

        if player_id != 'Not found':

            return HttpResponseRedirect(
                reverse(
                    'player-details-page',
                    args=[player_id],
                )
            )

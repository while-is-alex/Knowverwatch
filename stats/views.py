from OWLAPI import Owl
from django.shortcuts import render
from django.views import View


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

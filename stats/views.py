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

        try:
            team = Team.objects.get(name__icontains=search)
        except Team.DoesNotExist:
            team = None

        if team is not None:
            print('team found')
            return HttpResponseRedirect(
                reverse(
                    'team-details-page',
                    args=[team.slug]
                )
            )

        try:
            player = Player.objects.get(name__icontains=search)
        except Player.DoesNotExist:
            player = None

        if player is not None:
            print('player found')
            return HttpResponseRedirect(
                reverse(
                    'player-details-page',
                    args=[player.slug]
                )
            )

        return render(
            request,
            'stats/index.html',
        )
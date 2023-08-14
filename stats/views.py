from OWLAPI import Owl
from django.shortcuts import render
from django.views import View
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.core.paginator import Paginator
from .models import Team, Player, Segment, Match
from datetime import datetime

owl = Owl()


class HomeView(View):
    def get(self, request):

        return render(
            request,
            'stats/index.html',
        )


class TeamsView(View):
    def get(self, request):
        try:
            if request.GET['regions'] == 'all':
                all_teams = Team.objects.all().order_by('name')
            else:
                selected_region = request.GET['regions']
                print(selected_region)
                teams_in_region = Team.objects.filter(region=selected_region).order_by('name')
                all_teams = teams_in_region
        except KeyError:
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
        all_teams = Team.objects.all()
        selected_team = Team.objects.get(slug=slug)
        see_spoilers = request.session.get('see_spoilers')
        print(see_spoilers)

        # Sorts the players by role and finds their top 3 most played heroes
        roster = []
        for player in selected_team.players.all().order_by('role'):

            heroes_played = []
            for hero in player.heroes.keys():
                hero_details = {}
                try:
                    time_played = int(player.heroes[hero]['timePlayed'])
                except KeyError:
                    time_played = 0

                hero_details['name'] = hero
                hero_details['time_played'] = time_played

                heroes_played.append(hero_details)

            top3_heroes_by_time_played = sorted(heroes_played, key=lambda x: x['time_played'], reverse=True)[:3]

            roster.append((player, top3_heroes_by_time_played))

        # Fetches the most recent 5 matches for that team
        matches = Match.objects.filter(teams__has_key=selected_team.id).order_by('date').filter(date__year=2023)[::-1]
        matches_list = []
        for match in matches[:5]:
            match_details = {}
            team_one = list(match.teams.items())[0][1]
            team_two = list(match.teams.items())[1][1]
            match_details['home'] = team_one
            match_details['away'] = team_two
            match_details['date'] = match.date
            match_details['slug'] = match.slug
            matches_list.append(match_details)

        return render(
            request,
            'stats/team-details.html',
            {
                'all_teams': all_teams,
                'team': selected_team,
                'players': roster,
                'matches': matches_list,
                'see_spoilers': see_spoilers,
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

        heroes_played = list(selected_player.heroes)
        for hero in heroes_played:
            hero_name = hero
            print(hero_name)
            print(f'{selected_player.heroes[hero_name]}\n\n')

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


class MatchDetailsView(View):
    def get(self, request, slug):
        selected_match = Match.objects.get(slug=slug)

        return render(
            request,
            'stats/match-details.html',
            {
                'match': selected_match,
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


class SeeSpoilersView(View):
    def get(self, request, slug):
        if request.session.get('see_spoilers') is None:
            see_spoilers = False
        else:
            # if it's true, it turns into false, and vice-versa
            see_spoilers = not request.session.get('see_spoilers')

        request.session['see_spoilers'] = see_spoilers

        return HttpResponseRedirect(
            reverse(
                'team-details-page',
                args=[slug],
            )
        )
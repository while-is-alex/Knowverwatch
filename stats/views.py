from OWLAPI import Owl
from classes import Stats
from django.shortcuts import render
from django.views import View
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.core.paginator import Paginator
from .models import Team, Player, Segment, Match
from datetime import datetime

owl = Owl()
stats = Stats()


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

        # sorts the players by role and finds their top 3 most played heroes
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

            top3_heroes_by_time_played = sorted(
                heroes_played,
                key=lambda x: x['time_played'],
                reverse=True,
            )[:3]

            roster.append((player, top3_heroes_by_time_played))

        # fetches the 5 most recent matches for the selected team
        current_year = datetime.today().year

        matches = Match.objects.filter(
            teams__has_key=selected_team.id
        ).order_by('date').filter(
            date__year=current_year
        )[::-1]

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

        player_all_teams = selected_player.all_teams
        past_teams = []
        for team in player_all_teams:
            try:
                team = Team.objects.get(id=team['id'])

                if team in past_teams:
                    continue

                if team != selected_player.team:
                    past_teams.append(team)

            except Team.DoesNotExist:
                continue

        heroes_played_sorted = stats.sort_by_time_played(selected_player.heroes)
        heroes_played_list = list(heroes_played_sorted)

        heroes_details = []
        for hero_name in heroes_played_list:
            hero_stats = selected_player.heroes[hero_name]
            formatted_details = stats.format_details(hero_name, hero_stats)

            try:
                if formatted_details[1]:
                    heroes_details.append(formatted_details)
                else:
                    continue
            except TypeError:
                continue

        return render(
            request,
            'stats/player-details.html',
            {
                'player': selected_player,
                'past_teams': past_teams,
                'heroes': heroes_details,
            }
        )


class ComparePlayersView(View):
    def get(self, request):
        all_players = Player.objects.all().order_by('name')

        # checks if there were previously selected players for comparison
        if request.session.get('selected_player_a') is None:
            player_a = None
            player_a_heroes = None
        else:
            selected_player_a = request.session.get('selected_player_a')
            player_a = Player.objects.get(id=selected_player_a)
            player_a_heroes = request.session.get('selected_player_a_heroes')

        if request.session.get('selected_player_b') is None:
            player_b = None
            player_b_heroes = None
        else:
            selected_player_b = request.session.get('selected_player_b')
            player_b = Player.objects.get(id=selected_player_b)
            player_b_heroes = request.session.get('selected_player_b_heroes')

        # checks if a new player is being selected for comparison
        try:
            player_a = Player.objects.get(id=request.GET['player-a'])

            heroes_played_sorted = stats.sort_by_name(player_a.heroes)
            heroes_played_list = list(heroes_played_sorted)

            player_a_heroes = []
            for hero_name in heroes_played_list:
                hero_stats = player_a.heroes[hero_name]
                formatted_details = stats.format_details(hero_name, hero_stats)

                try:
                    if formatted_details[1]:
                        player_a_heroes.append(formatted_details)
                    else:
                        continue
                except TypeError:
                    continue

            request.session['selected_player_a'] = player_a.id
            request.session['selected_player_a_heroes'] = player_a_heroes
            request.session['selected_hero_a'] = None

        except KeyError:
            pass

        try:
            player_b = Player.objects.get(id=request.GET['player-b'])

            heroes_played_sorted = stats.sort_by_name(player_b.heroes)
            heroes_played_list = list(heroes_played_sorted)

            player_b_heroes = []
            for hero_name in heroes_played_list:
                hero_stats = player_b.heroes[hero_name]
                formatted_details = stats.format_details(hero_name, hero_stats)

                try:
                    if formatted_details[1]:
                        player_b_heroes.append(formatted_details)
                    else:
                        continue
                except TypeError:
                    continue

            request.session['selected_player_b'] = player_b.id
            request.session['selected_player_b_heroes'] = player_b_heroes
            request.session['selected_hero_b'] = None
        except KeyError:
            pass

        # checks if there were previously selected heroes for comparison
        if request.session.get('selected_hero_a') is None:
            hero_a = None
        else:
            hero_a = request.session.get('selected_hero_a')

        if request.session.get('selected_hero_b') is None:
            hero_b = None
        else:
            hero_b = request.session.get('selected_hero_b')

        # checks if a new hero is being selected for comparison
        try:
            selected_hero = request.GET['hero-a']

            for hero in player_a_heroes:
                hero_name = hero[0]
                if hero_name == selected_hero:
                    hero_a = hero
                    request.session['selected_hero_a'] = hero_a
        except KeyError:
            pass

        try:
            selected_hero = request.GET['hero-b']

            for hero in player_b_heroes:
                hero_name = hero[0]
                if hero_name == selected_hero:
                    hero_b = hero
                    request.session['selected_hero_b'] = hero_b
        except KeyError:
            pass

        return render(
            request,
            'stats/compare-players.html',
            {
                'all_players': all_players,
                'player_a': player_a,
                'player_a_heroes': player_a_heroes,
                'hero_a': hero_a,
                'player_b': player_b,
                'player_b_heroes': player_b_heroes,
                'hero_b': hero_b,
            }
        )


class MatchDetailsView(View):
    def get(self, request, slug):
        selected_match = Match.objects.get(slug=slug)

        home_team = Team.objects.get(id=list(selected_match.teams.items())[0][0])
        away_team = Team.objects.get(id=list(selected_match.teams.items())[1][0])

        try:
            home_team_final_score = int(list(selected_match.teams.items())[0][1]['score'])
        except KeyError:
            home_team_final_score = 0

        try:
            away_team_final_score = int(list(selected_match.teams.items())[1][1]['score'])
        except KeyError:
            away_team_final_score = 0

        see_spoilers = request.session.get('see_spoilers')

        games = list(selected_match.games.items())
        games_details_list = []
        for game in games:
            try:
                home_team_score = list(game[1]['teams'].items())[0][1]['score']
            except KeyError:
                home_team_score = 0

            try:
                away_team_score = list(game[1]['teams'].items())[1][1]['score']
            except KeyError:
                away_team_score = 0

            map_name = game[1]['map'].title().replace('-', ' ')
            if map_name == 'Esperanca':
                map_name = 'Esperança'

            game_details = {
                'order': int(game[1]['number']),
                'map': map_name,
                'home_team': Team.objects.get(id=list(game[1]['teams'].items())[0][1]['id']),
                'home_team_score': home_team_score,
                'away_team': Team.objects.get(id=list(game[1]['teams'].items())[1][1]['id']),
                'away_team_score': away_team_score,
            }
            games_details_list.append(game_details)

        sorted_games_list = sorted(
            games_details_list,
            key=lambda x: x['order'],
            reverse=False,
        )

        players_in_this_match = list(selected_match.players.items())
        players_list = []
        for player in players_in_this_match:
            player_details = {}
            player_details['player'] = Player.objects.get(id=player[1]['id'])
            player_details['team_id'] = player[1]['teamId']
            player_details['heroes_played'] = []
            for hero in list(player[1]['heroes'].items()):
                player_details['heroes_played'].append(hero[0].title())

            players_list.append(player_details)

        return render(
            request,
            'stats/match-details.html',
            {
                'match': selected_match,
                'home_team': home_team,
                'home_team_score': home_team_final_score,
                'away_team': away_team,
                'away_team_score': away_team_final_score,
                'games': sorted_games_list,
                'players': players_list,
                'see_spoilers': see_spoilers,
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

        try:
            Team.objects.get(slug=slug)

            return HttpResponseRedirect(
                reverse(
                    'team-details-page',
                    args=[slug],
                )
            )

        except Team.DoesNotExist:
            Match.objects.get(slug=slug)

            return HttpResponseRedirect(
                reverse(
                    'match-details-page',
                    args=[slug],
                )
            )

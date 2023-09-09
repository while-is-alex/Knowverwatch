from OWLAPI import Owl
from classes import Stats
from django.shortcuts import render, get_object_or_404
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
        season = Segment.objects.get(id='owl2-2023-regular')
        standings = season.standings

        standings_west = []
        standings_east = []

        for team in standings:
            if list(team['divisions'].keys())[0] == 'west':
                current_team = {
                    'team_object': Team.objects.get(id=team['teamId']),
                    'wins': int(team['gameWins']),
                    'losses': int(team['gameLosses']),
                    'win_rate': f"{round((int(team['gameWins']) / (int(team['gameWins']) + int(team['gameLosses']))) * 100)}%",
                    'matches_played': int(team['gameWins']) + int(team['gameLosses']),
                    'maps': f"{team['matchWins']}-{team['matchLosses']}-{team['gameTies']}",
                    'differential': int(team['gameDifferential']),
                }
                standings_west.append(current_team)

            elif list(team['divisions'].keys())[0] == 'east':
                current_team = {
                    'team_object': Team.objects.get(id=team['teamId']),
                    'wins': int(team['gameWins']),
                    'losses': int(team['gameLosses']),
                    'win_rate': f"{round((int(team['gameWins']) / (int(team['gameWins']) + int(team['gameLosses']))) * 100)}%",
                    'matches_played': int(team['gameWins']) + int(team['gameLosses']),
                    'maps': f"{team['matchWins']}-{team['matchLosses']}-{team['gameTies']}",
                    'differential': int(team['gameDifferential']),
                }
                standings_east.append(current_team)

        return render(
            request,
            'stats/index.html',
            {
                'teams_west': standings_west,
                'teams_east': standings_east,
            }
        )


class TeamsView(View):
    def get(self, request):
        try:
            if request.GET['regions'] == 'all':
                all_teams = Team.objects.all().order_by('name')

            else:
                selected_region = request.GET['regions']
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
        see_spoilers = request.session.get('see_spoilers')

        all_teams = Team.objects.all()
        selected_team = Team.objects.get(slug=slug)

        # sorts the team's players by role and finds their top 3 most played heroes
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
            team_one = list(match.teams.items())[0][1]
            team_two = list(match.teams.items())[1][1]

            match_details = {
                'home': team_one,
                'away': team_two,
                'date': match.date,
                'slug': match.slug
            }
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
        page_object = paginator.get_page(page_number)

        return render(
            request,
            'stats/players.html',
            {
                'page_obj': page_object,
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

            try:  # checks if the current hero was played long enough
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
        def get_previously_selected_player_and_heroes(session_key):
            player_id = request.session.get(session_key)

            if player_id is None:
                return None, None

            player = get_object_or_404(Player, id=player_id)
            heroes = request.session.get(f'{session_key}_heroes')

            return player, heroes

        player_a, player_a_heroes = get_previously_selected_player_and_heroes('selected_player_a')
        player_b, player_b_heroes = get_previously_selected_player_and_heroes('selected_player_b')

        # checks if a new player is being selected for comparison
        def get_selected_player(session_key):
            new_selected_player = Player.objects.get(id=request.GET[session_key])

            heroes_played_sorted = stats.sort_by_name(new_selected_player.heroes)
            heroes_played_list = list(heroes_played_sorted)

            new_selected_player_heroes = []
            for hero_name in heroes_played_list:
                hero_stats = new_selected_player.heroes[hero_name]
                formatted_details = stats.format_details(hero_name, hero_stats)

                try:
                    if formatted_details[1]:
                        new_selected_player_heroes.append(formatted_details)
                    else:
                        continue
                except TypeError:
                    continue

            if session_key == 'player-a':
                request.session['selected_player_a'] = new_selected_player.id
                request.session['selected_player_a_heroes'] = new_selected_player_heroes
                request.session['selected_hero_a'] = None
            elif session_key == 'player-b':
                request.session['selected_player_b'] = new_selected_player.id
                request.session['selected_player_b_heroes'] = new_selected_player_heroes
                request.session['selected_hero_b'] = None

            return new_selected_player, new_selected_player_heroes

        if request.GET.get('player-a'):
            player_a, player_a_heroes = get_selected_player('player-a')
        elif request.GET.get('player-b'):
            player_b, player_b_heroes = get_selected_player('player-b')

        # checks if there were previously selected heroes for comparison
        def get_previously_selected_hero(session_key):
            if request.session.get(session_key) is None:
                hero = None
            else:
                hero = request.session.get(session_key)

            return hero

        hero_a = get_previously_selected_hero('selected_hero_a')
        hero_b = get_previously_selected_hero('selected_hero_b')

        # checks if a new hero is being selected for comparison
        def get_selected_hero(session_key):
            selected_hero = request.GET.get(session_key)
            if selected_hero:
                for hero in player_a_heroes if session_key == 'hero-a' else player_b_heroes:
                    if hero[0] == selected_hero:
                        return hero
            return None

        if request.GET.get('hero-a'):
            hero_a = get_selected_hero('hero-a')
            request.session['selected_hero_a'] = hero_a
        elif request.GET.get('hero-b'):
            hero_b = get_selected_hero('hero-b')
            request.session['selected_hero_b'] = hero_b

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
        see_spoilers = request.session.get('see_spoilers')

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
            player_details = {
                'player': Player.objects.get(id=player[1]['id']),
                'team_id': player[1]['teamId'],
                'heroes_played': []
            }
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

        return HttpResponseRedirect(
            reverse(
                'home-page',
            )
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

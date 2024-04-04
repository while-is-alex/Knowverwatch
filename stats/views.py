from utilities.classes import Stats, UpdateDatabase
from django.shortcuts import render, get_object_or_404, redirect
from django.views import View
from django.http import HttpResponseNotFound, JsonResponse
from django.core.paginator import Paginator
from django.contrib import messages
from .models import Team, Player, Segment, Match
from datetime import datetime
from django.utils import timezone

stats = Stats()
update = UpdateDatabase()


def get_heroes_details(player, heroes_played):
    heroes_played_list = list(heroes_played)

    heroes_details = []
    for hero_name in heroes_played_list:
        hero_stats = player.heroes[hero_name]
        formatted_details = stats.format_details(hero_name, hero_stats)

        try:  # checks if the current hero was played long enough
            if formatted_details[1]:
                heroes_details.append(formatted_details)
            else:
                continue
        except TypeError:
            continue

    return heroes_details


class HomeView(View):
    def get(self, request):
        is_dark_mode = request.session.get('is_dark_mode', False)
        if request.session.get('see_spoilers') is None:
            see_spoilers = False
            request.session['see_spoilers'] = see_spoilers
        else:
            see_spoilers = request.session.get('see_spoilers')

        current_datetime = timezone.now()
        current_date = current_datetime.date()
        formatted_date_string = current_date.strftime('%d/%m/%Y')

        # uncomment to get the data for the current segment that's being played
        # current_segment = Segment.objects.filter(
        #     first_match__lte=current_datetime,
        #     last_match__gte=current_datetime,
        # ).first()
        current_segment = Segment.objects.get(id='owl2-2023-regular')
        current_segment_name = current_segment.name

        standings = current_segment.standings
        standings_west = self.get_teams_standings(standings, 'west')
        standings_east = self.get_teams_standings(standings, 'east')

        # updates the database asynchronously
        # update.update_segment_database(current_segment.id)
        # all_teams = Team.objects.all()
        # for team in all_teams:
        #     update.update_team_database(team.id)

        return render(
            request,
            'stats/index.html',
            {
                'is_dark_mode': is_dark_mode,
                'today': formatted_date_string,
                'see_spoilers': see_spoilers,
                'current_segment_name': current_segment_name,
                'teams_west': standings_west,
                'teams_east': standings_east,
            }
        )

    def get_teams_standings(self, standings, region):
        region_standings = []
        for team in standings:
            if list(team['divisions'].keys())[0] == region:
                current_team = {
                    'team_object': Team.objects.get(id=team['teamId']),
                    'wins': int(team['matchWins']),
                    'losses': int(team['matchLosses']),
                    'win_rate': f"{round((int(team['matchWins']) / (int(team['matchWins']) + int(team['matchLosses']))) * 100)}%",
                    'matches_played': int(team['matchWins']) + int(team['matchLosses']),
                    'maps': f"{team['gameWins']}-{team['gameLosses']}-{team['gameTies']}",
                    'differential': int(team['gameDifferential']),
                }
                region_standings.append(current_team)

        return region_standings


class TeamsView(View):
    def get(self, request):
        is_dark_mode = request.session.get('is_dark_mode', False)

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
                'is_dark_mode': is_dark_mode,
                'teams': all_teams,
            }
        )


class TeamDetailsView(View):
    def get(self, request, slug):
        is_dark_mode = request.session.get('is_dark_mode', False)
        see_spoilers = request.session.get('see_spoilers')

        try:
            selected_team = Team.objects.get(slug=slug)
            # update.update_team_database(selected_team.id)

            awards = selected_team.awards.all().order_by('year')

            # sorts the team's players by role and finds their top 3 most played heroes
            roster = [(player, self.get_top3_heroes(player))
                      for player in selected_team.players.all().order_by('role')]

            matches_list = self.get_team_matches(selected_team)
        except Team.DoesNotExist:
            return HttpResponseNotFound('Team not found')

        return render(
            request,
            'stats/team-details.html',
            {
                'is_dark_mode': is_dark_mode,
                'all_teams': Team.objects.all(),
                'team': selected_team,
                'awards': awards,
                'players': roster,
                'matches': matches_list,
                'see_spoilers': see_spoilers,
            }
        )

    def get_team_matches(self, team):
        current_year = datetime.today().year

        matches = Match.objects.filter(
            teams__has_key=team.id,
            date__year=current_year,
        ).order_by('-date')

        # updates matches in the database when the match doesn't have a winner
        # team_matches_ids = [match.id for match in matches if match.winner_id is None]
        # for match_id in team_matches_ids:
        #     update.update_match_database(match_id)

        matches_list = [{'home': team_values[0], 'away': team_values[1], 'date': match.date, 'slug': match.slug}
                        for match in matches for team_values in [list(match.teams.values())]]
        return matches_list

    def get_top3_heroes(self, player):
        heroes_played = []

        for hero, hero_stats in player.heroes.items():
            time_played = int(hero_stats.get('timePlayed', 0))

            if time_played > 0:
                heroes_played.append({'name': hero, 'time_played': time_played})

        return sorted(heroes_played, key=lambda x: x['time_played'], reverse=True)[:3]


class PlayersView(View):
    def get(self, request):
        is_dark_mode = request.session.get('is_dark_mode', False)
        all_players = Player.objects.all().order_by('name')

        paginator = Paginator(all_players, 20)
        page_number = request.GET.get('page')
        page_object = paginator.get_page(page_number)

        return render(
            request,
            'stats/players.html',
            {
                'is_dark_mode': is_dark_mode,
                'page_obj': page_object,
                'request': request,
            }
        )


class PlayerDetailsView(View):
    def get(self, request, slug):
        is_dark_mode = request.session.get('is_dark_mode')
        selected_player = Player.objects.get(slug=slug)
        # update.update_player_database(selected_player.id)

        awards = selected_player.awards.all().order_by('year')

        player_all_teams = selected_player.all_teams
        past_teams = self.get_past_teams(selected_player, player_all_teams)

        heroes_played_sorted_by_time = stats.sort_by_time_played(selected_player.heroes) if selected_player.heroes else []
        heroes_details = get_heroes_details(selected_player, heroes_played_sorted_by_time)

        return render(
            request,
            'stats/player-details.html',
            {
                'is_dark_mode': is_dark_mode,
                'player': selected_player,
                'awards': awards,
                'past_teams': past_teams,
                'heroes': heroes_details,
            }
        )

    def get_past_teams(self, player, teams):
        past_teams = []
        for team in teams:
            try:
                team = Team.objects.get(id=team['id'])

                if team in past_teams:
                    continue

                if team != player.team:
                    past_teams.append(team)

            except Team.DoesNotExist:
                continue

        return past_teams


class ComparePlayersView(View):
    def get(self, request):
        is_dark_mode = request.session.get('is_dark_mode')
        all_players = Player.objects.all().order_by('name')

        # checks if there were previously selected players for comparison
        player_a, player_a_heroes = self.get_previously_selected_player_and_heroes('selected_player_a')
        player_b, player_b_heroes = self.get_previously_selected_player_and_heroes('selected_player_b')

        # checks if a new player is being selected for comparison
        if request.GET.get('player-a'):
            player_a, player_a_heroes = self.get_selected_player('player-a')
        elif request.GET.get('player-b'):
            player_b, player_b_heroes = self.get_selected_player('player-b')

        # checks if there were previously selected heroes for comparison
        hero_a = self.request.session.get('selected_hero_a')
        hero_b = self.request.session.get('selected_hero_b')

        # checks if a new hero is being selected for comparison
        if request.GET.get('hero-a'):
            hero_a = self.get_selected_hero('hero-a', player_a_heroes)
            request.session['selected_hero_a'] = hero_a
        elif request.GET.get('hero-b'):
            hero_b = self.get_selected_hero('hero-b', player_b_heroes)
            request.session['selected_hero_b'] = hero_b

        return render(
            request,
            'stats/compare-players.html',
            {
                'is_dark_mode': is_dark_mode,
                'all_players': all_players,
                'player_a': player_a,
                'player_a_heroes': player_a_heroes,
                'hero_a': hero_a,
                'player_b': player_b,
                'player_b_heroes': player_b_heroes,
                'hero_b': hero_b,
            }
        )

    def get_previously_selected_player_and_heroes(self, session_key):
        player_id = self.request.session.get(session_key)

        if player_id is None:
            return None, None

        player = get_object_or_404(Player, id=player_id)
        heroes = self.request.session.get(f'{session_key}_heroes')

        return player, heroes

    def get_selected_player(self, session_key):
        selected_player = Player.objects.get(id=self.request.GET[session_key])

        heroes_played_sorted_by_name = stats.sort_by_name(selected_player.heroes)
        selected_player_heroes = get_heroes_details(selected_player, heroes_played_sorted_by_name)

        if session_key == 'player-a':
            self.request.session['selected_player_a'] = selected_player.id
            self.request.session['selected_player_a_heroes'] = selected_player_heroes
            self.request.session['selected_hero_a'] = None
        elif session_key == 'player-b':
            self.request.session['selected_player_b'] = selected_player.id
            self.request.session['selected_player_b_heroes'] = selected_player_heroes
            self.request.session['selected_hero_b'] = None

        return selected_player, selected_player_heroes

    def get_selected_hero(self, session_key, heroes):
        selected_hero = self.request.GET.get(session_key)
        if selected_hero:
            for hero in heroes:
                if hero[0] == selected_hero:
                    return hero

        return None


class MatchDetailsView(View):
    def get(self, request, slug):
        is_dark_mode = request.session.get('is_dark_mode')
        see_spoilers = request.session.get('see_spoilers')

        selected_match = Match.objects.get(slug=slug)
        # update.update_match_database(selected_match.id)

        teams_data = list(selected_match.teams.values())

        home_team = Team.objects.get(id=teams_data[0]['id'])
        away_team = Team.objects.get(id=teams_data[1]['id'])

        home_team_final_score = int(teams_data[0].get('score', 0))
        away_team_final_score = int(teams_data[1].get('score', 0))

        games = list(selected_match.games.items())
        sorted_games_details_list = self.get_games_details(games)

        players_in_this_match = list(selected_match.players.items())
        players_details_list = self.get_players_details(players_in_this_match)

        return render(
            request,
            'stats/match-details.html',
            {
                'is_dark_mode': is_dark_mode,
                'match': selected_match,
                'home_team': home_team,
                'home_team_score': home_team_final_score,
                'away_team': away_team,
                'away_team_score': away_team_final_score,
                'games': sorted_games_details_list,
                'players': players_details_list,
                'see_spoilers': see_spoilers,
            }
        )

    def get_games_details(self, games):
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

        sorted_games_details_list = sorted(
            games_details_list,
            key=lambda x: x['order'],
            reverse=False,
        )

        return sorted_games_details_list

    def get_players_details(self, players):
        players_details_list = []
        for player in players:
            player_details = {
                'player': Player.objects.get(id=player[1]['id']),
                'team_id': player[1]['teamId'],
                'heroes_played': []
            }
            for hero in list(player[1]['heroes'].items()):
                player_details['heroes_played'].append(hero[0].title())

            players_details_list.append(player_details)

        return players_details_list


class GameView(View):
    def get(self, request, slug):
        is_dark_mode = request.session.get('is_dark_mode', False)

        return render(
            request,
            'stats/match-details.html',
            {
                'is_dark_mode': is_dark_mode,
            }
        )


class SearchView(View):
    def search_players(self, search):
        return Player.objects.filter(name__icontains=search).first()

    def search_teams(self, search):
        return Team.objects.filter(name__icontains=search).first()

    def get(self, request):
        search = request.GET.get('search', '').strip().lower()

        player_found = self.search_players(search)
        team_found = self.search_teams(search)

        if team_found:
            return redirect(
                'team-details-page',
                slug=team_found.slug,
            )

        elif player_found:
            return redirect(
                'player-details-page',
                slug=player_found.slug,
            )

        else:
            no_results_message = "No results found for your search."
            messages.info(request, no_results_message)

            return redirect(
                'home-page',
            )


class SeeSpoilersView(View):
    def get(self, request, slug):
        if request.session.get('see_spoilers') is None:
            see_spoilers = False

        else:
            # if it's true, it turns into false, and vice-versa
            see_spoilers = not request.session.get('see_spoilers')

        request.session['see_spoilers'] = see_spoilers

        referring_page = request.META.get('HTTP_REFERER', '/')

        if slug is not None:
            return redirect(
                referring_page,
                slug=slug,
            )

        else:
            return redirect(
                referring_page,
            )


class ToggleModeView(View):
    def post(self, request):
        dark_mode = not request.session.get('is_dark_mode', False)
        request.session['is_dark_mode'] = dark_mode

        return JsonResponse({'dark_mode': dark_mode})

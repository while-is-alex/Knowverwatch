import requests
from dotenv import load_dotenv
import os


class Owl:
    def __init__(self):
        """Generates a token for the current session."""
        load_dotenv()

        token_endpoint = 'https://oauth.battle.net/token'
        token_response = requests.post(
            token_endpoint,
            {
                'grant_type': 'client_credentials',
                'client_id': os.getenv('CLIENT_ID'),
                'client_secret': os.getenv('CLIENT_SECRET'),
             }
        )
        token_response.raise_for_status()
        token_data = token_response.json()

        self.token = token_data['access_token']
        self.base_endpoint = f'https://us.api.blizzard.com'
        self.params = {
            'access_token': self.token
        }

    def summary(self):
        """Returns all the information in the API's database."""
        summary_data_api = '/owl/v1/owl2'

        summary_response = requests.get(
            url=f'{self.base_endpoint}{summary_data_api}',
            params=self.params
        )
        summary_response.raise_for_status()
        summary_data = summary_response.json()

        return summary_data

    def get_player_id(self, player_name):
        """Receives a player name and returns their id."""
        data = self.summary()

        all_players = data['players'].items()
        for player in all_players:
            name = player[1]['name']
            if name.lower() == player_name.lower():
                return player[1]['id']

    def players(self, player_id):
        """Receives a player id and returns all data about that player."""
        players_api = '/owl/v1/players/'

        player_response = requests.get(
            url=f'{self.base_endpoint}{players_api}{player_id}',
            params=self.params
        )
        player_response.raise_for_status()

        try:
            player_data = player_response.json()

            return player_data

        except ValueError:
            return 'Player not found.'

    def all_players(self):
        data = self.summary()
        all_players = list(data['players'].items())

        return all_players

    def get_team_id(self, team_name):
        """Receives a team name and returns its id."""
        data = self.summary()

        all_teams = data['teams'].items()
        for team in all_teams:
            if team_name.title() in team[1]['name']:
                return team[1]['id']

    def teams(self, team_id):
        """Receives a team id and returns all data about that team."""
        teams_api = '/owl/v1/teams/'

        team_response = requests.get(
            url=f'{self.base_endpoint}{teams_api}{team_id}',
            params=self.params
        )
        team_response.raise_for_status()
        try:
            team_data = team_response.json()

            return team_data

        except ValueError:
            return 'Team not found.'

    def all_teams(self):
        data = self.summary()
        all_teams = list(data['teams'].items())

        return all_teams

    def get_segment_id(self, segment_name):
        """Receives a tournament name and returns its id."""
        data = self.summary()

        segments = data['segments'].items()
        for segment in segments:
            name = segment[1]['name'].lower()
            segment_name = segment_name.lower()

            if set(segment_name.split()).issubset(name.split()):
                return segment[1]['id']

    def segments(self, segment_id):
        """Receives a tournament id and returns all data about that tournament."""
        segments_api = '/owl/v1/segments/'

        segment_response = requests.get(
            url=f'{self.base_endpoint}{segments_api}{segment_id}',
            params=self.params
        )
        segment_response.raise_for_status()
        try:
            segment_data = segment_response.json()

            return segment_data

        except ValueError:
            return 'Segment not found.'

    def get_match_id(self, team_1_name, team_2_name):
        """Receives 2 team names and returns the ids for all matches in between those teams."""
        t1 = self.get_team_id(team_1_name)
        t2 = self.get_team_id(team_2_name)

        data = self.summary()

        all_matches = []
        matches = data['matches'].items()
        for match in matches:
            teams = list(match[1]['teams'].keys())

            if {t1, t2}.issubset(teams):
                all_matches.append(match[1]['id'])

        return all_matches

    def matches(self, match_id):
        """Receives a match id and returns all data about that match."""
        matches_api = '/owl/v1/matches/'

        match_response = requests.get(
            url=f'{self.base_endpoint}{matches_api}{match_id}',
            params=self.params
        )
        match_response.raise_for_status()
        try:
            match_data = match_response.json()

            return match_data

        except ValueError:
            return 'Match not found.'

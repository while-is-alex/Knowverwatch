import requests
from dotenv import load_dotenv
import os


class Owl:
    def __init__(self):
        """Generates an authorization token for the current session and
        initializes the endpoint and params for the http request."""
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
        """Returns a summary from all the data in the Overwatch League API's database."""
        summary_api_endpoint = '/owl/v1/owl2'

        summary_response = requests.get(
            url=f'{self.base_endpoint}{summary_api_endpoint}',
            params=self.params
        )
        summary_response.raise_for_status()
        summary_data = summary_response.json()

        return summary_data

    def get_all_players(self):
        """Returns data about all the players in the Overwatch League."""
        summary_data = self.summary()
        all_players = list(summary_data['players'].items())

        return all_players

    def get_player_id(self, player_name):
        """Receives a player name and returns their id.
        If a player is not found, returns None."""
        summary_data = self.summary()

        all_players = summary_data['players'].items()
        for player in all_players:
            name = player[1]['name']
            if name.lower() == player_name.lower():
                return player[1]['id']

        return None

    def get_player(self, player_id):
        """Receives a player id and returns all data about that player."""
        players_api_endpoint = '/owl/v1/players/'

        player_response = requests.get(
            url=f'{self.base_endpoint}{players_api_endpoint}{player_id}',
            params=self.params
        )
        player_response.raise_for_status()

        try:
            player_data = player_response.json()

            return player_data

        except ValueError:

            return None

    def get_all_teams(self):
        """Returns data about all the teams in the Overwatch League."""
        summary_data = self.summary()
        all_teams = list(summary_data['teams'].items())

        return all_teams

    def get_team_id(self, team_name):
        """Receives a team name and returns its id.
        If a team is not found, returns None."""
        summary_data = self.summary()

        all_teams = summary_data['teams'].items()
        for team in all_teams:
            if team_name.title() in team[1]['name']:
                return team[1]['id']

        return None

    def get_team(self, team_id):
        """Receives a team id and returns all data about that team."""
        teams_api_endpoint = '/owl/v1/teams/'

        team_response = requests.get(
            url=f'{self.base_endpoint}{teams_api_endpoint}{team_id}',
            params=self.params
        )
        team_response.raise_for_status()

        try:
            team_data = team_response.json()

            return team_data

        except ValueError:

            return None

    def get_segment_id(self, segment_name):
        """Receives a tournament name and returns its id."""
        summary_data = self.summary()

        segments = summary_data['segments'].items()
        for segment in segments:
            name = segment[1]['name'].lower()
            segment_name = segment_name.lower()

            if set(segment_name.split()).issubset(name.split()):
                return segment[1]['id']

        return None

    def get_segment(self, segment_id):
        """Receives a tournament id and returns all data about that tournament."""
        segments_api_endpoint = '/owl/v1/segments/'

        segment_response = requests.get(
            url=f'{self.base_endpoint}{segments_api_endpoint}{segment_id}',
            params=self.params
        )
        segment_response.raise_for_status()

        try:
            segment_data = segment_response.json()

            return segment_data

        except ValueError:

            return None

    def get_match_id(self, team_1_name, team_2_name):
        """Receives 2 team names and returns the ids for all matches in between those teams."""
        t1 = self.get_team_id(team_1_name)
        t2 = self.get_team_id(team_2_name)

        summary_data = self.summary()

        matches_list = []
        matches = summary_data['matches'].items()
        for match in matches:
            teams = list(match[1]['teams'].keys())

            if {t1, t2}.issubset(teams):
                matches_list.append(match[1]['id'])

        return matches_list

    def get_match(self, match_id):
        """Receives a match id and returns all data about that match."""
        matches_api_endpoint = '/owl/v1/matches/'

        match_response = requests.get(
            url=f'{self.base_endpoint}{matches_api_endpoint}{match_id}',
            params=self.params
        )
        match_response.raise_for_status()

        try:
            match_data = match_response.json()

            return match_data

        except ValueError:

            return None

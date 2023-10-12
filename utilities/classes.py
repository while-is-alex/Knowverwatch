from .OWLAPI import OverwatchLeague
from stats.models import Team, Player, Segment, Match
from datetime import date, datetime, timezone


class Stats:
    def split_camel_case(self, camel_case_string):
        """Splits a camelCase string into words and returns a title-cased string."""

        words = []

        current_word = camel_case_string[0]
        for character in camel_case_string[1:]:
            if current_word[-1].islower() and character.isupper():
                words.append(current_word)
                current_word = character
            else:
                current_word += character

        words.append(current_word)
        resulting_string = ' '.join(words).title()

        return resulting_string

    def sort_by_name(self, stats_dictionary):
        """Sorts a dictionary of hero statistics by hero names alphabetically."""

        heroes_sorted_by_name = dict(sorted(stats_dictionary.items()))

        return heroes_sorted_by_name

    def sort_by_time_played(self, stats_dictionary):
        """Sorts a dictionary of hero statistics by the time played, in descending order."""

        def get_time_played(current_hero):
            return current_hero[1].get('timePlayed', 0)

        heroes_sorted_by_time_played = dict(
            sorted(
                stats_dictionary.items(),
                key=lambda x: get_time_played(x),
                reverse=True,
            )
        )

        return heroes_sorted_by_time_played

    def get_stats_per_10(self, stats_list):
        """Calculates and returns statistics per 10 minutes of playtime."""

        hero_minutes_played = 0

        for stat in stats_list:
            if stat['name'] == 'Time Played':
                hero_minutes_played = stat['value']

        if hero_minutes_played == 0:
            return stats_list

        list_of_stats_per_10 = []
        for stat in stats_list:
            stat_name = stat['name']
            stat_value = stat['value']

            if stat_name == 'Time Played':
                list_of_stats_per_10.append(stat)
            else:
                if stat_name in [
                    'Damage Done',
                    'Damage Taken',
                    'Healing Done',
                    'Shots Hit',
                    'Time Spent On Fire',
                ]:
                    stat_per_10 = round((stat_value / hero_minutes_played) * 10)
                else:
                    stat_per_10 = round((stat_value / hero_minutes_played) * 10, 2)

                stat['value'] = stat_per_10
                list_of_stats_per_10.append(stat)

        return list_of_stats_per_10

    def format_details(self, hero_name, stats_dictionary):
        """Formats hero statistics and returns them as a dictionary."""

        stats_dictionary_keys = stats_dictionary.keys()

        stat_order = [
            'Time Played',
            'Eliminations',
            'Final Blows',
            'Deaths',
            'Damage Done',
            'Healing Done',
            'Damage Taken',
            'Shots Hit',
            'Critical Hits',
            'Ults Earned',
            'Ults Used',
            'Time Spent On Fire',
            'Solo Kills',
        ]

        stats_list = []
        for key in stats_dictionary_keys:
            stat_name = self.split_camel_case(key)

            if stat_name == 'Hero Damage Done':
                stat_name = 'Damage Done'

            stat_value = round((stats_dictionary[key]), 2)
            if stat_name == 'Time Played':
                stat_value = round(int(stats_dictionary[key]) / 60)  # seconds to minutes

            current_stat = {
                'name': stat_name,
                'value': stat_value,
            }

            if stat_name in stat_order:
                index = stat_order.index(stat_name)
                stats_list.insert(index, current_stat)
            else:
                stats_list.append(current_stat)

        stats_list_per_10 = self.get_stats_per_10(stats_list)

        for stat in stats_list_per_10:
            if stat['name'] == 'Time Played' and stat['value'] > 1:
                hero_details = (hero_name.title(), stats_list)

                return hero_details


class UpdateDatabase:
    def update_team_database(self, team_id):
        print(f'updating team {team_id}')
        owl = OverwatchLeague()
        team_response = owl.get_team(team_id)

        alternate_ids = team_response.get('alternateIds', [])
        alternate_id = alternate_ids[0]['id'] if alternate_ids else None

        name = team_response['name']
        code = team_response['code']
        logo = team_response['logo']
        icon = team_response['icon']

        unformatted_primary_color = team_response.get('primaryColor')
        primary_color = f'#{unformatted_primary_color}' if unformatted_primary_color else None

        unformatted_secondary_color = team_response.get('secondaryColor')
        secondary_color = f'#{unformatted_secondary_color}' if unformatted_secondary_color else None

        Team.objects.filter(id=team_id).update(
            alternate_id=alternate_id,
            name=name,
            code=code,
            logo=logo,
            icon=icon,
            primary_color=primary_color,
            secondary_color=secondary_color,
        )

        current_year = datetime.today().year

    def update_player_database(self, player_id):
        print(f'updating player {player_id}')
        owl = OverwatchLeague()
        player_response = owl.get_player(player_id)

        alternate_id = None
        if 'alternateIds' in player_response:
            alternate_id_list = player_response['alternateIds']
            if alternate_id_list:
                alternate_id = int(alternate_id_list[0]['id'])

        headshot_url = player_response.get(
            'headshotUrl',
            'https://images.blz-contentstack.com/v3/assets/blt321317473c90505c/bltcdcb764c3287821b/601b44aa3689c30bf149261e/Generic_Player_Icon.png'
        )
        if headshot_url == 'https://images.blz-contentstack.com':
            headshot_url = 'https://images.blz-contentstack.com/v3/assets/blt321317473c90505c/bltcdcb764c3287821b/601b44aa3689c30bf149261e/Generic_Player_Icon.png'

        name = player_response['name']
        first_name = player_response.get('givenName')
        last_name = player_response.get('familyName')

        role_mapping = {
            'offense': 'DPS',
            'tank': 'TANK',
            'support': 'SUPPORT'
        }
        role = role_mapping.get(player_response.get('role'))

        team = None
        current_teams_list = player_response.get('currentTeams', [])
        for current_team in current_teams_list:
            try:
                team = Team.objects.get(id=current_team)
                break
            except Team.DoesNotExist:
                continue

        number = player_response.get('number')

        all_teams = player_response.get('teams', [])
        heroes = player_response.get('heroes', [])
        stats = player_response.get('stats', {})
        segment_stats = player_response.get('segmentStats', {})

        Player.objects.filter(id=player_id).update(
            alternate_id=alternate_id,
            headshot_url=headshot_url,
            name=name,
            first_name=first_name,
            last_name=last_name,
            role=role,
            team=team,
            number=number,
            all_teams=all_teams,
            heroes=heroes,
            stats=stats,
            segment_stats=segment_stats,
        )

    def parse_timestamp(self, timestamp):
        if timestamp is not None:
            return datetime.fromtimestamp(timestamp / 1000, tz=timezone.utc)
        return None

    def update_segment_database(self, segment_id):
        print(f'updating segment {segment_id}')
        owl = OverwatchLeague()
        segment_response = owl.get_segment(segment_id)

        name = segment_response['name']
        season = segment_response['seasonId']
        teams = segment_response.get('teams')
        players = segment_response.get('players')
        standings = segment_response.get('standings')
        first_match = self.parse_timestamp(segment_response.get('firstMatchStart'))
        last_match = self.parse_timestamp(segment_response.get('lastMatchStart'))

        Segment.objects.filter(id=segment_id).update(
            name=name,
            season=season,
            teams=teams,
            players=players,
            standings=standings,
            first_match=first_match,
            last_match=last_match,
        )

    def update_match_database(self, match_id):
        print(f'updating match {match_id}')
        owl = OverwatchLeague()
        match_response = owl.get_match(match_id)

        season = int(match_response['seasonId'])
        segment = Segment.objects.get(id=match_response['segmentId'])

        date_unformatted = match_response['localScheduledDate']
        split_date = date_unformatted.split('-')
        date_object = date(int(split_date[0]), int(split_date[1]), int(split_date[2]))

        start_timestamp = self.parse_timestamp(match_response.get('startTimestamp'))
        end_timestamp = self.parse_timestamp(match_response.get('endTimestamp'))
        state = match_response.get('state')
        teams = match_response.get('teams')
        games = match_response.get('games')
        players = match_response.get('players')

        winner_id = match_response.get('winner')
        if winner_id is not None:
            winner_id = int(winner_id)

        match_url = None
        for region in match_response.get('hyperlinks', []):
            if region.get('contentLanguage') == 'en':
                match_url = region.get('value')

        Match.objects.filter(id=match_id).update(
            season=season,
            segment=segment,
            date=date_object,
            start_timestamp=start_timestamp,
            end_timestamp=end_timestamp,
            state=state,
            teams=teams,
            games=games,
            players=players,
            winner_id=winner_id,
            match_url=match_url,
        )

    def create_team_in_database(self, team_id, team_data):
        print(f'creating team {team_id}')
        alternate_ids = team_data.get('alternateIds', [])
        alternate_id = alternate_ids[0]['id'] if alternate_ids else None

        name = team_data['name']
        code = team_data['code']
        logo = team_data['logo']
        icon = team_data['icon']

        unformatted_primary_color = team_data.get('primaryColor')
        primary_color = f'#{unformatted_primary_color}' if unformatted_primary_color else None

        unformatted_secondary_color = team_data.get('secondaryColor')
        secondary_color = f'#{unformatted_secondary_color}' if unformatted_secondary_color else None

        new_team = Team(
            id=team_id,
            alternate_id=alternate_id,
            name=name,
            code=code,
            region=None,
            logo=logo,
            icon=icon,
            primary_color=primary_color,
            secondary_color=secondary_color,
        )
        new_team.save()

    def create_player_in_database(self, player_id, player_data):
        print(f'creating player {player_id}')
        alternate_id = None
        if 'alternateIds' in player_data:
            alternate_id_list = player_data['alternateIds']
            if alternate_id_list:
                alternate_id = int(alternate_id_list[0]['id'])

        headshot_url = player_data.get(
            'headshotUrl',
            'https://images.blz-contentstack.com/v3/assets/blt321317473c90505c/bltcdcb764c3287821b/601b44aa3689c30bf149261e/Generic_Player_Icon.png'
        )
        if headshot_url == 'https://images.blz-contentstack.com':
            headshot_url = 'https://images.blz-contentstack.com/v3/assets/blt321317473c90505c/bltcdcb764c3287821b/601b44aa3689c30bf149261e/Generic_Player_Icon.png'

        name = player_data['name']
        first_name = player_data.get('givenName')
        last_name = player_data.get('familyName')

        role_mapping = {
            'offense': 'DPS',
            'tank': 'TANK',
            'support': 'SUPPORT'
        }
        role = role_mapping.get(player_data.get('role'))

        team = None
        current_teams_list = player_data.get('currentTeams', [])
        for current_team in current_teams_list:
            try:
                team = Team.objects.get(id=current_team)
                break
            except Team.DoesNotExist:
                continue

        number = player_data.get('number')
        all_teams = player_data.get('teams', [])
        heroes = player_data.get('heroes', [])
        stats = player_data.get('stats', {})
        segment_stats = player_data.get('segmentStats', {})

        new_player = Player(
            id=player_id,
            alternate_id=alternate_id,
            headshot_url=headshot_url,
            name=name,
            first_name=first_name,
            last_name=last_name,
            role=role,
            team=team,
            number=number,
            all_teams=all_teams,
            heroes=heroes,
            stats=stats,
            segment_stats=segment_stats,
        )
        new_player.save()

    def create_segment_in_database(self, segment_id, segment_data):
        print(f'creating segment {segment_id}')
        name = segment_data.get('name')
        season = segment_data.get('seasonId')
        teams = segment_data.get('teams')
        players = segment_data.get('players')
        standings = segment_data.get('standings')
        first_match = self.parse_timestamp(segment_data.get('firstMatchStart'))
        last_match = self.parse_timestamp(segment_data.get('lastMatchStart'))

        new_segment = Segment(
            id=segment_id,
            name=name,
            season=season,
            teams=teams,
            players=players,
            standings=standings,
            first_match=first_match,
            last_match=last_match,
        )
        new_segment.save()

    def create_match_in_database(self, match_id, match_data):
        print(f'creating match {match_id}')
        season = int(match_data['seasonId'])
        segment_id = match_data.get('segmentId')
        if segment_id is not None:
            segment = Segment.objects.get(id=segment_id)
        else:
            segment = None

        date_unformatted = match_data['localScheduledDate']
        split_date = date_unformatted.split('-')
        date_object = date(int(split_date[0]), int(split_date[1]), int(split_date[2]))

        start_timestamp = self.parse_timestamp(match_data.get('startTimestamp'))
        end_timestamp = self.parse_timestamp(match_data.get('endTimestamp'))
        state = match_data['state']
        teams = match_data.get('teams')
        games = match_data.get('games')
        players = match_data.get('players')

        winner_id = match_data.get('winner')
        if winner_id is not None:
            winner_id = int(winner_id)

        match_url = None
        for region in match_data.get('hyperlinks', []):
            if region.get('contentLanguage') == 'en':
                match_url = region.get('value')

        new_match = Match(
            id=match_id,
            season=season,
            segment=segment,
            date=date_object,
            start_timestamp=start_timestamp,
            end_timestamp=end_timestamp,
            state=state,
            teams=teams,
            games=games,
            players=players,
            winner_id=winner_id,
            match_url=match_url,
        )
        new_match.save()

    def update_database(self, model_class, data_items, create_in_database_function, update_database_function):
        for item_id, item_data in data_items.items():
            try:
                model_class.objects.get(id=item_id)
                update_database_function(item_id)
            except model_class.DoesNotExist:
                create_in_database_function(item_id, item_data)

    def update_the_whole_database(self):
        print('updating the whole database')
        owl = OverwatchLeague()
        response = owl.summary()

        self.update_database(Team, response['teams'], self.create_team_in_database, self.update_team_database)
        self.update_database(Player, response['players'], self.create_player_in_database, self.update_player_database)
        self.update_database(Segment, response['segments'], self.create_segment_in_database, self.update_segment_database)

        all_segments = Segment.objects.all()
        for segment in all_segments:
            print(segment.name)
            response = owl.get_segment(segment.id)

            self.update_database(Match, response['matches'], self.create_match_in_database, self.update_match_database)

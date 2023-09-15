from celery import shared_task
from .models import Team, Player, Segment, Match
from utilities.OWLAPI import OverwatchLeague
from datetime import date, datetime, timezone

owl = OverwatchLeague()


@shared_task
def update_team_database(team_id, team_matches_ids):
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
    secondary_color = f'#{unformatted_primary_color}' if unformatted_secondary_color else None

    Team.objects.filter(id=team_id).update(
        alternate_id=alternate_id,
        name=name,
        code=code,
        logo=logo,
        icon=icon,
        primary_color=primary_color,
        secondary_color=secondary_color,
    )

    for match_id in team_matches_ids:
        update_match_database(match_id)


@shared_task
def update_player_database(player_id):
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


def parse_timestamp(timestamp):
    if timestamp is not None:
        return datetime.fromtimestamp(timestamp / 1000, tz=timezone.utc)
    return None


@shared_task
def update_segment_database(segment_id):
    segment_response = owl.get_segment(segment_id)

    name = segment_response['name']
    season = segment_response['seasonId']
    teams = segment_response['teams']
    players = segment_response['players']
    standings = segment_response.get('standings')
    first_match = parse_timestamp(segment_response.get('firstMatchStart'))
    last_match = parse_timestamp(segment_response.get('lastMatchStart'))

    Segment.objects.filter(id=segment_id).update(
        name=name,
        season=season,
        teams=teams,
        players=players,
        standings=standings,
        first_match=first_match,
        last_match=last_match,
    )


@shared_task
def update_match_database(match_id):
    match_response = owl.get_match(match_id)

    season = int(match_response['seasonId'])
    segment = Segment.objects.get(id=match_response['segmentId'])

    date_unformatted = match_response['localScheduledDate']
    split_date = date_unformatted.split('-')
    date_object = date(int(split_date[0]), int(split_date[1]), int(split_date[2]))

    start_timestamp = parse_timestamp(match_response.get('startTimestamp'))
    end_timestamp = parse_timestamp(match_response.get('endTimestamp'))
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


@shared_task
def create_team_in_database(team_id, team_data):
    alternate_ids = team_data.get('alternateIds', [])
    alternate_id = alternate_ids[0]['id'] if alternate_ids else None

    name = team_data['name']
    code = team_data['code']
    logo = team_data['logo']
    icon = team_data['icon']

    unformatted_primary_color = team_data.get('primaryColor')
    primary_color = f'#{unformatted_primary_color}' if unformatted_primary_color else None

    unformatted_secondary_color = team_data.get('secondaryColor')
    secondary_color = f'#{unformatted_primary_color}' if unformatted_secondary_color else None

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


@shared_task
def create_player_in_database(player_id, player_data):
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


@shared_task
def create_segment_in_database(segment_id, segment_data):
    name = segment_data.get('name')
    season = segment_data.get('seasonId')
    teams = segment_data.get('teams')
    players = segment_data.get('players')
    standings = segment_data.get('standings')
    first_match = parse_timestamp(segment_data.get('firstMatchStart'))
    last_match = parse_timestamp(segment_data.get('lastMatchStart'))

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


@shared_task
def create_match_in_database(match_id, match_data):
    season = int(match_data['seasonId'])
    segment_id = match_data.get('segmentId')
    if segment_id is not None:
        segment = Segment.objects.get(id=segment_id)
    else:
        segment = None

    date_unformatted = match_data['localScheduledDate']
    split_date = date_unformatted.split('-')
    date_object = date(int(split_date[0]), int(split_date[1]), int(split_date[2]))

    start_timestamp = parse_timestamp(match_data.get('startTimestamp'))
    end_timestamp = parse_timestamp(match_data.get('endTimestamp'))
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


@shared_task
def update_database(model_class, data_items, create_in_database_function):
    for item_id, item_data in data_items.items():
        try:
            model_class.objects.get(id=item_id)
        except model_class.DoesNotExist:
            create_in_database_function(item_id, item_data)


@shared_task
def update_the_whole_database():
    response = owl.summary()

    update_database(Team, response['teams'], create_team_in_database)
    update_database(Player, response['players'], create_player_in_database)
    update_database(Segment, response['segments'], create_segment_in_database)
    update_database(Match, response['matches'], create_match_in_database)

from celery import shared_task
from .models import Team, Player, Segment, Match
from utilities.OWLAPI import OverwatchLeague
from datetime import date, datetime, timezone

owl = OverwatchLeague()


@shared_task
def update_team_database(team_id, team_matches_ids):
    team_response = owl.get_team(team_id)
    try:
        alternate_id = int(team_response['alternateIds'][0]['id'])
    except IndexError:
        alternate_id = None

    name = team_response['name']
    code = team_response['code']
    logo = team_response['logo']
    icon = team_response['icon']
    try:
        primary_color = f"#{team_response['primaryColor']}"
    except KeyError:
        primary_color = None

    try:
        secondary_color = f"#{team_response['secondaryColor']}"
    except KeyError:
        secondary_color = None

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

    try:
        alternate_id = int(player_response['alternateIds'][0]['id'])
    except IndexError:
        alternate_id = None

    headshot_url = player_response.get('headshotUrl', 'https://images.blz-contentstack.com/v3/assets/blt321317473c90505c/bltcdcb764c3287821b/601b44aa3689c30bf149261e/Generic_Player_Icon.png')
    if headshot_url == 'https://images.blz-contentstack.com':
        headshot_url = 'https://images.blz-contentstack.com/v3/assets/blt321317473c90505c/bltcdcb764c3287821b/601b44aa3689c30bf149261e/Generic_Player_Icon.png'

    name = player_response['name']
    first_name = player_response.get('givenName', None)
    last_name = player_response.get('familyName', None)

    try:
        role = player_response['role']
    except KeyError:
        role = None

    if role == 'offense':
        role = 'DPS'
    else:
        if role:
            role = role.upper()

    current_teams_list = player_response['currentTeams']
    team = None
    if current_teams_list:
        current_team = current_teams_list[0]
        try:
            team = Team.objects.get(id=current_team)
            print(team)
        except Team.DoesNotExist:
            try:
                current_team = current_teams_list[1]
                team = Team.objects.get(id=current_team)
                print(team)
            except Team.DoesNotExist:
                team = None
    try:
        number = int(player_response['number'])
    except KeyError:
        number = None

    all_teams = player_response['teams']
    heroes = player_response['heroes']
    stats = player_response['stats']
    segment_stats = player_response['segmentStats']

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


@shared_task
def update_segment_database(segment_id):
    segment_response = owl.get_segment(segment_id)

    name = segment_response['name']
    season = segment_response['seasonId']
    teams = segment_response['teams']
    players = segment_response['players']
    try:
        standings = segment_response['standings']
    except KeyError:
        standings = None

    try:
        first_match_seconds = segment_response['firstMatchStart'] / 1000
        first_match = datetime.fromtimestamp(first_match_seconds, tz=timezone.utc)
    except KeyError:
        first_match = None

    try:
        last_match_seconds = segment_response['lastMatchStart'] / 1000
        last_match = datetime.fromtimestamp(last_match_seconds, tz=timezone.utc)
    except KeyError:
        last_match = None

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

    try:
        start_seconds = match_response['startTimestamp'] / 1000
        start_timestamp = datetime.fromtimestamp(start_seconds, tz=timezone.utc)
    except KeyError:
        start_timestamp = None

    try:
        end_seconds = match_response['endTimestamp'] / 1000
        end_timestamp = datetime.fromtimestamp(end_seconds, tz=timezone.utc)
    except KeyError:
        end_timestamp = None

    state = match_response['state']
    teams = match_response['teams']
    games = match_response['games']
    players = match_response['players']

    try:
        if match_response['winner'] is not None:
            winner_id = int(match_response['winner'])
        else:
            winner_id = None
    except KeyError:
        winner_id = None

    match_url = None
    for region in match_response['hyperlinks']:
        if region['contentLanguage'] == 'en':
            match_url = region['value']

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
def create_team_in_database(team_items):
    team_id = team_items[0]

    try:
        alternate_id = int(team_items[1]['alternateIds'][0]['id'])
    except IndexError:
        alternate_id = None

    name = team_items[1]['name']
    code = team_items[1]['code']
    logo = team_items[1]['logo']
    icon = team_items[1]['icon']

    try:
        primary_color = f"#{team_items[1]['primaryColor']}"
    except KeyError:
        primary_color = None

    try:
        secondary_color = f"#{team_items[1]['secondaryColor']}"
    except KeyError:
        secondary_color = None

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
def create_player_in_database(player_items):
    player_id = int(player_items[0])

    try:
        alternate_id = int(player_items[1]['alternateIds'][0]['id'])
    except IndexError:
        alternate_id = None

    headshot_url = player_items[1].get('headshotUrl', 'https://images.blz-contentstack.com/v3/assets/blt321317473c90505c/bltcdcb764c3287821b/601b44aa3689c30bf149261e/Generic_Player_Icon.png')
    if headshot_url == 'https://images.blz-contentstack.com':
        headshot_url = 'https://images.blz-contentstack.com/v3/assets/blt321317473c90505c/bltcdcb764c3287821b/601b44aa3689c30bf149261e/Generic_Player_Icon.png'

    name = player_items[1]['name']
    first_name = player_items[1].get('givenName', None)
    last_name = player_items[1].get('familyName', None)

    try:
        role = player_items[1]['role']
    except KeyError:
        role = None

    if role == 'offense':
        role = 'DPS'
    else:
        if role:
            role = role.upper()

    try:
        current_teams_list = player_items[1]['currentTeams']
    except KeyError:
        current_teams_list = None

    team = None
    if current_teams_list:
        try:
            current_team = current_teams_list[0]
            team = Team.objects.get(id=current_team)
            print(team)
        except Team.DoesNotExist:
            try:
                current_team = current_teams_list[1]
                team = Team.objects.get(id=current_team)
                print(team)
            except Team.DoesNotExist:
                team = None

    try:
        number = int(player_items[1]['number'])
    except KeyError:
        number = None

    all_teams = player_items[1]['teams']

    try:
        heroes = player_items[1]['heroes']
    except KeyError:
        heroes = None

    try:
        stats = player_items[1]['stats']
    except KeyError:
        stats = None

    try:
        segment_stats = player_items[1]['segmentStats']
    except KeyError:
        segment_stats = None

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
def create_segment_in_database(segment_items):
    segment_id = segment_items[0]

    name = segment_items[1]['name']
    season = segment_items[1]['seasonId']
    teams = segment_items[1]['teams']
    players = segment_items[1]['players']

    try:
        standings = segment_items[1]['standings']
    except KeyError:
        standings = None

    try:
        first_match_seconds = segment_items[1]['firstMatchStart'] / 1000
        first_match = datetime.fromtimestamp(first_match_seconds, tz=timezone.utc)
    except KeyError:
        first_match = None

    try:
        last_match_seconds = segment_items[1]['lastMatchStart'] / 1000
        last_match = datetime.fromtimestamp(last_match_seconds, tz=timezone.utc)
    except KeyError:
        last_match = None

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
def create_match_in_database(match_items):
    match_id = match_items[0]

    season = int(match_items[1]['seasonId'])
    segment = Segment.objects.get(id=match_items[1]['segmentId'])

    date_unformatted = match_items[1]['localScheduledDate']
    split_date = date_unformatted.split('-')
    date_object = date(int(split_date[0]), int(split_date[1]), int(split_date[2]))

    try:
        start_seconds = match_items[1]['startTimestamp'] / 1000
        start_timestamp = datetime.fromtimestamp(start_seconds, tz=timezone.utc)
    except KeyError:
        start_timestamp = None

    try:
        end_seconds = match_items[1]['endTimestamp'] / 1000
        end_timestamp = datetime.fromtimestamp(end_seconds, tz=timezone.utc)
    except KeyError:
        end_timestamp = None

    state = match_items[1]['state']

    try:
        teams = match_items[1]['teams']
    except KeyError:
        teams = None

    try:
        games = match_items[1]['games']
    except KeyError:
        games = None

    try:
        players = match_items[1]['players']
    except KeyError:
        players = None

    try:
        if match_items[1]['winner'] is not None:
            winner_id = int(match_items[1]['winner'])
        else:
            winner_id = None
    except KeyError:
        winner_id = None

    match_url = None
    for region in match_items[1]['hyperlinks']:
        if region['contentLanguage'] == 'en':
            match_url = region['value']

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
def update_the_whole_database():
    response = owl.summary()

    teams = response['teams']
    for team in teams.items():
        try:
            Team.objects.get(id=team[0])
        except Team.DoesNotExist:
            create_team_in_database(team)

    players = response['players']
    for player in players.items():
        try:
            Player.objects.get(id=player[0])
        except Player.DoesNotExist:
            create_player_in_database(player)

    segments = response['segments']
    for segment in segments.items():
        try:
            Segment.objects.get(id=segment[0])
        except Segment.DoesNotExist:
            create_segment_in_database(segment)

    matches = response['matches']
    for match in matches.items():
        try:
            Match.objects.get(id=match[0])
        except Match.DoesNotExist:
            create_match_in_database(match)

from celery import shared_task
from .models import Team, Player, Segment, Match
from utilities.OWLAPI import OverwatchLeague
from datetime import date

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
    first_name = player_response.get('givenName', '')
    last_name = player_response.get('familyName', '')
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

    number = int(player_response.get('number', 0))
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
    pass


@shared_task
def update_match_database(match_id):
    match_response = owl.get_match(match_id)

    season = int(match_response['seasonId'])
    segment = Segment.objects.get(id=match_response['segmentId'])

    date_unformatted = match_response['localScheduledDate']
    split_date = date_unformatted.split('-')
    date_object = date(int(split_date[0]), int(split_date[1]), int(split_date[2]))

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

    print(f'Season: {season}\n'
          f'Segment: {segment}\n'
          f'Date: {date_object}\n'
          f'State: {state}\n'
          f'Games: {games}\n'
          f'Players: {players}\n'
          f'Winner: {winner_id}\n'
          f'URL: {match_url}')

    Match.objects.filter(id=match_id).update(
        season=season,
        segment=segment,
        date=date,
        state=state,
        teams=teams,
        games=games,
        players=players,
        winner_id=winner_id,
        match_url=match_url,
    )


@shared_task
def update_all_teams_database(match_id):
    pass

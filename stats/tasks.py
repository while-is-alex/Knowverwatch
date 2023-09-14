from celery import shared_task
from .models import Team, Player, Segment, Match
from utilities.OWLAPI import OverwatchLeague

owl = OverwatchLeague()


@shared_task
def update_team_database(team_id):
    pass


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
    pass


@shared_task
def update_all_teams_database(match_id):
    pass

from celery import shared_task
from .models import Team, Player, Segment, Match
from utilities.OWLAPI import OverwatchLeague
import time

owl = OverwatchLeague()


@shared_task
def update_team_database(team_id):
    pass


@shared_task
def update_player_database(player_id):
    summary = owl.summary()
    player = owl.get_player(player_id)
    print(player)


@shared_task
def update_segment_database(segment_id):
    pass


@shared_task
def update_match_database(match_id):
    pass


@shared_task
def update_all_teams_database(match_id):
    pass

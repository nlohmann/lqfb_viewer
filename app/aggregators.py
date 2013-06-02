# -*- coding: utf-8 -*-
from app import helper, cache, app, models, db
from flask import flash
import urllib, urllib2, json
from utils import api_load, api_load_all, db_load
import json
from math import ceil
from filter import future_date_filter
from datetime import datetime, timedelta
import pytz
import iso8601

# policy: complete object
# phase: {'admission_time', 'discussion_time', 'verification_time', 'voting_time'}
def delta_phase(policy, phase):
    delta = timedelta(0)
    if 'minutes' in policy[phase]:
        delta += timedelta(minutes=policy[phase]['minutes'])
    if 'hours' in policy[phase]:
        delta += timedelta(hours=policy[phase]['hours'])
    if 'days' in policy[phase]:
        delta += timedelta(days=policy[phase]['days'])
    if 'years' in policy[phase]:
        delta += timedelta(days=policy[phase]['years'] * 365)
    return delta


def issue_progress(issue, policy):
    def get_progress(begin, duration):
        now = datetime.now(tz=pytz.timezone('Europe/Berlin'))
        seconds_since_begin = (now-begin).total_seconds()
        
        return round(100.0 * (seconds_since_begin / duration.total_seconds()), 2)

    result = dict()
    result['admission_progress'] = 0.0
    result['discussion_progress'] = 0.0
    result['verification_progress'] = 0.0
    result['voting_progress'] = 0.0

    if issue['state'] == 'admission':
        begin = iso8601.parse_date(issue['created']).astimezone(pytz.timezone('Europe/Berlin'))
        duration = delta_phase(policy, 'admission_time')
        result['admission_progress'] = get_progress(begin, duration)

    if issue['state'] == 'discussion':
        begin = iso8601.parse_date(issue['accepted']).astimezone(pytz.timezone('Europe/Berlin'))
        duration = delta_phase(policy, 'discussion_time')
        result['admission_progress'] = 100.0
        result['discussion_progress'] = get_progress(begin, duration)

    if issue['state'] == 'verification':
        begin = iso8601.parse_date(issue['half_frozen']).astimezone(pytz.timezone('Europe/Berlin'))
        duration = delta_phase(policy, 'verification_time')
        result['admission_progress'] = 100.0
        result['discussion_progress'] = 100.0
        result['verification_progress'] = get_progress(begin, duration)

    if issue['state'] == 'voting':
        begin = iso8601.parse_date(issue['fully_frozen']).astimezone(pytz.timezone('Europe/Berlin'))
        duration = delta_phase(policy, 'voting_time')
        result['admission_progress'] = 100.0
        result['discussion_progress'] = 100.0
        result['verification_progress'] = 100.0
        result['voting_progress'] = get_progress(begin, duration)

    if issue['state'] in ['canceled_revoked_before_accepted', 'canceled_issue_not_accepted', 'canceled_no_initiative_admitted']:
        result['admission_progress'] = 100.0

    if issue['state'] == 'canceled_after_revocation_during_discussion':
        result['admission_progress'] = 100.0
        result['discussion_progress'] = 100.0

    if issue['state'] == 'canceled_after_revocation_during_verification':
        result['admission_progress'] = 100.0
        result['discussion_progress'] = 100.0
        result['verification_progress'] = 100.0

    if issue['state'] in ['finished_without_winner','finished_with_winner', 'calculation']:
        result['admission_progress'] = 100.0
        result['discussion_progress'] = 100.0
        result['verification_progress'] = 100.0
        result['voting_progress'] = 100.0

    return result


def policy_bars(policy):
    result = dict()

    result['total_time_seconds_max'] = 0
    for phase in ['admission_time', 'discussion_time', 'verification_time', 'voting_time']:
        result[phase + '_seconds'] = int(delta_phase(policy, phase).total_seconds())
        result['total_time_seconds_max'] += result[phase + '_seconds']

    result['total_time_seconds_min'] = result['total_time_seconds_max'] - result['admission_time_seconds']

    result['voting_time_percentage'] = 100.0
    for phase in ['admission_time', 'discussion_time', 'verification_time']:
        result[phase + '_percentage'] = round(100.0 * (float(result[phase + '_seconds']) / float(result['total_time_seconds_max'])), 2)
        result['voting_time_percentage'] -= result[phase + '_percentage']

    result['voting_time_percentage'] = round(result['voting_time_percentage'], 2)

    return result


#############################################################################

def issue_aggregated(issue_id, session=None):
    result = db_load('/issue', q={'issue_id': issue_id})['result'][0]

    # add prospected ends of the timestamps
    result['accepted_deadline'] = result['accepted'] if result['accepted'] != None else future_date_filter(result['created'], result['admission_time'])
    result['half_frozen_deadline'] = result['half_frozen'] if result['half_frozen'] != None else future_date_filter(result['accepted_deadline'], result['discussion_time'])
    result['fully_frozen_deadline'] = result['fully_frozen'] if result['fully_frozen'] != None else future_date_filter(result['half_frozen_deadline'], result['verification_time'])
    result['closed_deadline'] = result['closed'] if result['closed'] != None else future_date_filter(result['fully_frozen_deadline'], result['voting_time'])

    # calculate voter percentage
    result['voter_percentage'] = round(100.0 * float(result['voter_count']) / float(result['population']), 2) if result['voter_count'] != None else None

    # add all initiatives of the issue
    result['initiatives'] = db_load('/initiative', q={'issue_id': issue_id})['result']

    # add the area
    result['area'] = db_load('/area', q={'area_id': result['area_id']})['result'][0]

    # add the unit
    result['unit'] = db_load('/unit', q={'unit_id': result['area']['unit_id']})['result'][0]

    # add the policy
    result['policy'] = db_load('/policy', q={'policy_id': result['policy_id']})['result'][0]
    result['policy']['issue_quorum_percentage'] = round(100.0 * float(result['policy']['issue_quorum_num']) / float(result['policy']['issue_quorum_den']), 2)
    result['policy']['initiative_quorum_percentage'] = round(100.0 * float(result['policy']['initiative_quorum_num']) / float(result['policy']['initiative_quorum_den']), 2)

    # add absolute numbers for the quorums
    result['issue_quorum'] = int(ceil((float(result['policy']['issue_quorum_num']) / float(result['policy']['issue_quorum_den'])) * result['population']))
    result['initiative_quorum'] = int(ceil((float(result['policy']['initiative_quorum_num']) / float(result['policy']['initiative_quorum_den'])) * result['population']))

    # add bars
    bars = policy_bars(result['policy'])
    result['policy'] = dict(result['policy'].items() + bars.items())

    # add interested members (needs a session)
    result['interest'] = dict()
    try:
        for snapshot in ['latest', 'end_of_admission', 'half_freeze', 'full_freeze']:
            result['interest'][snapshot] = api_load('/interest', q={'issue_id': issue_id, 'snapshot': snapshot}, session=session)['result']
    except:
        pass

    # add progress
    progress = issue_progress(issue=result, policy=result['policy'])
    result = dict(result.items() + progress.items())

    # add battle
    if result['status_quo_schulze_rank'] != None:
        result['battle'] = api_load('/battle', q={'issue_id': issue_id})['result']
        result['battle_table'] = dict()
        for b in result['battle']:
            winner = b['winning_initiative_id'] if b['winning_initiative_id'] != None else 0
            loser = b['losing_initiative_id'] if b['losing_initiative_id'] != None else 0

            if not winner in result['battle_table']:
                result['battle_table'][winner] = dict()

            result['battle_table'][winner][loser] = b['count']

    return result

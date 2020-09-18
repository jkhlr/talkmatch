import logging

from django.utils import timezone

from match.models import Group, Participant, Match
from match.sms_adapter import SmsAdapter

logger = logging.getLogger(__name__)


def create_participant(phone_number, message):
    groups = [
        group for group in Group.objects.filter(matched=False)
        if group.keyword in message
    ]
    if not groups:
        logger.warning(f'Invalid message (group not found): {message}')
        return

    group = groups[0]
    can_call = group.caller_hint in message

    participant = Participant.objects.create(
        phone_number=phone_number,
        can_call=can_call,
        group=groups
    )
    logger.info(f'Participant {participant} created')
    notify_registered(participant)
    return participant


def notify_registered(participant):
    SmsAdapter.send_message(
        participant.phone_number,
        participant.group.registered_notification
    )
    logger.info(f'Participant {participant} notified for registration')


# ---

def match(group):
    if group.matched:
        raise ValueError(f'Group {group} is already matched')

    participants = group.participants.all()
    participants_calling = set(
        participant for participant in participants
        if participant.can_call
    )
    participants_not_calling = set(
        participant for participant in participants
        if not participant.can_call
    )

    rest = None
    while len(participants_calling):
        if not len(participants_not_calling):
            rest = participants_calling
            logger.debug(f'More calling participants for group {group}')
            break
        create_match(
            participants_calling.pop(),
            participants_not_calling.pop()
        )

    if rest is None:
        rest = participants_not_calling
        logger.debug(f'More non-calling participants for group {group}')

    while len(rest) > 1:
        create_match(rest.pop(), rest.pop())

    if rest:
        logger.debug(f'One participant of group {group} has no partner')
        create_match(rest.pop())

    group.matched = True
    group.save()
    logger.info(f'Group {group} matched')


def create_match(participant1, participant2=None):
    group = participant1.group
    assert participant2 is None or participant2.group == group

    match = Match.objects.create(group=group)

    participant1.match = match
    participant1.save()
    if participant2:
        participant2.match = match
        participant2.save()
    logger.info(f'Match {match} created')

    notify_match(match)
    return match


def notify_match(match):
    group = match.group
    participant1 = match.participants.filter(can_call=True).first()
    if participant1 is None:
        logger.debug(f'Match {match} has two non-calling participants')
        participant1 = match.participants.first()
    participant2 = match.participants.exclude(id=participant1.id).first()

    if participant2 is None:
        logger.debug(f'Participant {participant1} paired with backup number')
        participant2_phone_number = group.backup_number
    else:
        participant2_phone_number = participant2.phone_number

    message1 = group.match_notification_calling.format(
        phone_number=participant2_phone_number
    )
    message2 = group.match_notification_called.format(
        phone_number=participant1.phone_number
    )

    SmsAdapter.send_message(participant1.phone_number, message1)
    SmsAdapter.send_message(participant2_phone_number, message2)
    logger.info(f'Match {match} notified')


def goodbye(group):
    if group.goodbye_sent:
        raise ValueError(f'Goodbye is already sent for Group {group}')

    for participant in group.participants.all():
        SmsAdapter.send_message(
            participant.phone_number,
            group.goodbye_notification
        )
    group.goodbye_sent = True
    group.save()
    logger.info(f'Group {group} sent goodbye')


# ---

def execute_cron_actions():
    logger.info(f'Executing cron actions')
    for group in Group.objects.filter(matched=False):
        if group.match_time and timezone.now() >= group.match_time:
            logger.info(f'Match time reached for group {group}')
            match(group)
    for group in Group.objects.filter(goodbye_sent=False):
        if group.goodbye_time and timezone.now() >= group.goodbye_time:
            logger.info(f'Goodbye time reached for group {group}')
            goodbye(group)

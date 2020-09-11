from django.conf import settings
from django.utils import timezone

from match.models import Group, Participant, Match
from match.sms_adapter import send_message


def create_participant(phone_number, message):
    messaged_cleaned = message[len(settings.GLOBAL_KEYWORD):].strip()
    groups = [
        group for group in Group.objects.filter(matched=False)
        if group.keyword in messaged_cleaned
    ]
    if not groups:
        raise ValueError(f'Invalid message (group not found): {message}')
    # TODO: put into settings
    can_call = 'anrufer' in messaged_cleaned

    participant = Participant.objects.create(
        phone_number=phone_number,
        can_call=can_call,
        group=groups[0]
    )
    notify_registered(participant)
    return participant


def notify_registered(participant):
    send_message(
        participant.phone_number,
        participant.group.registered_notification
    )


# ---

def match(group):
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
            break
        create_match(
            participants_calling.pop(),
            participants_not_calling.pop()
        )

    if rest is None:
        rest = participants_not_calling

    while len(rest) > 1:
        create_match(rest.pop(), rest.pop())

    # TODO notify lonely person

    group.matched = True
    group.save()


def create_match(participant1, participant2):
    group = participant1.group
    assert participant2.group == group

    match = Match.objects.create(group=group)

    participant1.match = match
    participant1.save()
    participant2.match = match
    participant2.save()

    notify_match(match)
    return match


def notify_match(match):
    group = match.group
    participant1 = match.participants.filter(can_call=True).first()
    if participant1 is None:
        participant1 = match.participants.first()
    participant2 = match.participants.exclude(id=participant1.id).first()

    message1 = group.match_notification_calling.format(
        phone_number=participant2.phone_number
    )
    message2 = group.match_notification_called.format(
        phone_number=participant1.phone_number
    )

    send_message(participant1.phone_number, message1)
    send_message(participant2.phone_number, message2)


def notify_goodbye(group):
    for participant in group.participants.all():
        # TODO: what about lonely person?
        send_message(participant.phone_number, group.goodbye_notification)
    group.goodbye_sent = True
    group.save()


# ---

def check_execute_actions():
    for group in Group.objects.filter(matched=False):
        if timezone.now() >= group.match_time:
            match(group)
    for group in Group.objects.filter(goodbye_sent=False):
        if timezone.now() >= group.goodbye_time:
            notify_goodbye(group)
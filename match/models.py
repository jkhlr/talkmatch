from django.db import models
from django.utils import timezone


class Group(models.Model):
    keyword = models.CharField(max_length=100)
    caller_hint = models.CharField(max_length=100)
    backup_number = models.CharField(max_length=100)
    match_time = models.DateTimeField(null=True, blank=True)
    matched = models.BooleanField()
    goodbye_time = models.DateTimeField(null=True, blank=True)
    goodbye_sent = models.BooleanField()
    registered_notification = models.TextField(
        default="Registered!"
    )
    match_notification_calling = models.TextField(
        default="Matched with {phone_number}! Please call"
    )
    match_notification_called = models.TextField(
        default="Matched with {phone_number}! You will be called"
    )
    goodbye_notification = models.TextField(
        default="Thanks for participating!"
    )

    def __str__(self):
        return self.keyword


class Match(models.Model):
    created = models.DateTimeField(default=timezone.now)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)

    def __str__(self):
        return '& '.join(self.participants.all())


class Participant(models.Model):
    phone_number = models.CharField(max_length=100)
    can_call = models.BooleanField()
    group = models.ForeignKey(
        Group,
        related_name='participants',
        on_delete=models.CASCADE
    )
    match = models.ForeignKey(
        Match,
        null=True,
        related_name='participants',
        on_delete=models.SET_NULL
    )

    @property
    def matched(self):
        return bool(self.match)

    def __str__(self):
        return self.phone_number

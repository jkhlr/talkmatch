from django.db import models
from django.utils import timezone


class Group(models.Model):
    keyword_help = ('Keyword für diese Veranstaltung. Dieses Keyword muss '
                   'irgendwo in der Anmeldungs-SMS vorkommen. ' 
                   'Groß- und Kleinschreibung wird hierbei nicht ' 
                   'berücksichtigt. ACHTUNG: Unabhängig von diesem Keyword '
                   'muss jede Anmeldungs-SMS entweder mit "Gespraech" oder '
                   '"Nachgespraech" (ohne Anführungszeichen) anfangen. '
                   'Auch hier ist Groß- und Kleinschreibung egal.')
    keyword = models.CharField(max_length=100, help_text=keyword_help)
    caller_hint_help = ('Keyword für Menschen, die eine Flatrate haben und ' 
                       'gerne andere Menschen anrufen können. Kommt dieses ' 
                       'Wort in einer Anmeldungs-SMS vor, wird versucht '
                       'diese mit Personen zu matchen, die keine Flatrate '
                       'haben.')
    caller_hint = models.CharField(max_length=100, help_text=caller_hint_help)
    backup_number_help = ('Diese Nummer kommt zum Einsatz, wenn sich eine '
                         'ungerade Anzahl an Gesprächsteilnehmenden anmeldet. '
                         'Dann wird eine Person mit dieser Nummer gematched.')
    backup_number = models.CharField(max_length=100,
                                     help_text=backup_number_help)
    match_time_help = ('Zeitpunkt, zu dem automatisch ein Match aller bis dahin'
                      ' angemeldeten Menschen vorgenommen wird. ACHTUNG: Ist ' 
                      'ein Match ausgelöst worden, ist eine weitere Anmeldung '
                      'nicht mehr möglich, es sei denn es wird zuvor das ' 
                      'Häkchen bei "matched" entfernt. Dieses Feld kann auch ' 
                      'freigelassen werden. Dann kann immernoch mit dem' 
                      ' "Match" Button rechts oben ein Match ausgelöst werden.')
    match_time = models.DateTimeField(null=True,
                                      blank=True,
                                      help_text=match_time_help)
    matched = models.BooleanField()
    goodbye_time_help = ('Zeitpunkt, zu dem die Goodbye Nachricht verschickt ' 
                        'wird. Kann auch leergelassen werden, falls keine ' 
                        'Goodbye Nachricht gesendet werden soll oder diese '
                        'manuell mit dem Goodbye Button rechts oben ' 
                        'verschickt werden soll.')
    goodbye_time = models.DateTimeField(null=True,
                                        blank=True,
                                        help_text=goodbye_time_help)
    goodbye_sent = models.BooleanField()
    registered_help = ('Text für SMS, die als direkte Antwort an jede Person ' 
                      'verschickt wird, die sich erfolgreich angemeldet hat.')
    registered_notification = models.TextField(
        default="Registered!",
        help_text=registered_help
    )
    match_calling_help = ('Text für SMS, die zum Match-Zeitpunkt an alle ' 
                         'Anrufenden versendet wird. ACHTUNG: Im Text muss ' 
                         'unbedingt "{phone_number}" (ohne Anführungszeichen) ' 
                         'vorkommen. Dies wird dann mit der Nummer des Matches '
                         'ersetzt.' )
    match_notification_calling = models.TextField(
        default="Matched with {phone_number}! Please call",
        help_text=match_calling_help
    )
    match_called_help = ('Text für SMS, die zum Match-Zeitpunkt an alle '
                         'Angerufenen versendet wird. ACHTUNG: Im Text muss '
                         'unbedingt "{phone_number}" (ohne Anführungszeichen) '
                         'vorkommen. Dies wird dann mit der Nummer des Matches '
                         'ersetzt.')
    match_notification_called = models.TextField(
        default="Matched with {phone_number}! You will be called",
        help_text=match_called_help
    )
    goodbye_notification_help = ('Nachricht, die zum Goodbye-Zeitpunkt oder ' 
                                'bei Klick auf Button "Goodbye" an alle ' 
                                'Teilnehmenden versendet wird.')
    goodbye_notification = models.TextField(
        default="Thanks for participating!",
        help_text=goodbye_notification_help
    )

    def __str__(self):
        return self.keyword


class Match(models.Model):
    created = models.DateTimeField(default=timezone.now)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)

    def __str__(self):
        return '& '.join(
            str(participant)
            for participant
            in self.participants.all()
        )

    class Meta:
        verbose_name_plural = 'Matches'


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

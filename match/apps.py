from django.apps import AppConfig




class MatchConfig(AppConfig):
    name = 'match'

    def ready(self):
        from match.controller import create_participant
        from match.sms_adapter import SmsAdapter
        SmsAdapter.set_callback(create_participant)

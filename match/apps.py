from django.apps import AppConfig
from django.contrib.admin import AdminSite
from django.contrib.admin.apps import AdminConfig


class MatchConfig(AppConfig):
    name = 'match'

    def ready(self):
        from match.controller import create_participant
        from match.sms_adapter import SmsAdapter
        SmsAdapter.set_callback(create_participant)


class MatchAdminSite(AdminSite):
    index_template = 'admin_index.html'


class MatchAdminConfig(AdminConfig):
    default_site = 'match.apps.MatchAdminSite'

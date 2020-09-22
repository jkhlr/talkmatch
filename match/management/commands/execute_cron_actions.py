from django.core.management.base import BaseCommand

from match.controller import execute_cron_actions


class Command(BaseCommand):
    def handle(self, *args, **options):
        execute_cron_actions()
        self.stdout.write('All cron actions were executed')

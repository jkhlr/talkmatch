from django.core.management.base import BaseCommand

from match.sms_adapter import SmsAdapter


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('phone_number', type=str)
        parser.add_argument('message', type=str)

    def handle(self, *args, phone_number=None, message=None, **options):
        self.stdout.write(f'SMS from {phone_number} received: "{message}')
        SmsAdapter.receive_callback(phone_number, message)

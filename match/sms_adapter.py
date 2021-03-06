import logging

import requests
from django.conf import settings
from django.http import HttpResponse
from django.utils.datastructures import MultiValueDictKeyError
from django.views import View

logger = logging.getLogger(__name__)


class SmsAdapter(View):
    API_URL = 'https://gateway.sms77.io/api/sms'

    receive_callback = None

    @classmethod
    def set_callback(cls, callback):
        cls.receive_callback = callback
        return callback

    @classmethod
    def on_receive(cls, phone_number, message):
        logger.info(f'SMS from {phone_number}: "{message}"')

        if cls.receive_callback is None:
            logger.debug(f'No callback registered')
            return

        if not (phone_number.startswith('+') or phone_number.startswith('00')):
            phone_number = f'+{phone_number}'

        logger.debug(
            f'Executing callback: {cls.receive_callback} with arguments '
            f'phone_number={phone_number}, message={message}'
        )
        cls.receive_callback(phone_number, message)

    @classmethod
    def send_message(cls, phone_number, message):
        logger.info(f'Sending SMS to {phone_number}: {message}')

        if settings.SMS_API_DEBUG:
            logger.warning('SMS_API_DEBUG == True: no SMS was sent.')
            return

        parameters = {
            'p': settings.SMS_API_KEY,
            'to': phone_number,
            'text': message
        }
        response = requests.get(cls.API_URL, params=parameters)
        if response.status_code != 200:
            raise ValueError(
                f'API error (HTTP {response.status_code}): {response.content}'
            )

    def get(self, request):
        try:
            phone_number = request.GET['sender']
            message = request.GET['text']
        except MultiValueDictKeyError:
            return HttpResponse('Invalid Request', status=400)

        self.__class__.on_receive(phone_number, message)
        return HttpResponse('OK', status=200)

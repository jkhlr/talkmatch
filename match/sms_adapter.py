import requests
from django.http import HttpResponse


def dummy_callback(*args):
    raise NotImplementedError()


receive_callback = dummy_callback


def set_callback(callback):
    global receive_callback
    receive_callback = callback


def send_message(phone_number, message):
    parameters = {
        # TODO: put into settings
        "p": "API KEY",
        "to": phone_number,
        "text": message
    }
    return requests.get(
        # TODO: put into settings
        "https://gateway.sms77.io/api/sms",
        params=parameters
    )


def receive_message(request):
    if request.method != "GET":
        return HttpResponse(f"Method not allowed: {request.method}", status=502)
    # TODO validate parameters
    phone_number = request.GET['sender']
    message = request.GET['text']
    receive_callback(phone_number, message)
    return HttpResponse("200 OK", status=200)

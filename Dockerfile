FROM python:3.8-alpine as app

RUN apk add --no-cache tini

ENV BASE_DIR=/var/app
WORKDIR $BASE_DIR
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY manage.py manage.py
COPY talkmatch talkmatch
COPY match match

ENTRYPOINT ["/sbin/tini", "--"]


FROM app as web

ENV DJANGO_STATIC_ROOT=$BASE_DIR/static
RUN mkdir $DJANGO_STATIC_ROOT
RUN DJANGO_COLLECTSTATIC=1 python manage.py collectstatic --noinput

EXPOSE 8000
CMD gunicorn talkmatch.wsgi \
    --name talkmatch \
    --bind 0.0.0.0:8000 \
    --workers 3 \
    --log-level=debug \
    --access-logfile - \
    --error-logfile -

FROM app as cron

ENV CRON_COMMAND="$BASE_DIR/manage.py execute_cron_actions"
RUN echo "* * * * * $CRON_COMMAND" > /etc/crontabs/root
CMD crond -f

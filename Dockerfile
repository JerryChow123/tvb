FROM python:3.10.4-alpine3.14 as base

RUN apk add --update tzdata



FROM python:3.10.4-alpine3.14

RUN adduser -D tvb

WORKDIR /home/tvb

COPY requirements.txt requirements.txt
RUN apk add --no-cache --update gcc musl-dev libffi-dev openssl-dev
RUN python3 -m venv venv
RUN venv/bin/pip3 install --upgrade pip
RUN venv/bin/pip3 install -r requirements.txt
RUN venv/bin/pip3 install gunicorn

COPY app app
COPY migrations migrations
COPY tvb.py config.py run.py boot.sh app.db ./
RUN chmod +x boot.sh

ENV FLASK_APP run.py

COPY --from=base /usr/share/zoneinfo /usr/share/zoneinfo
ENV TZ=Asia/Hong_Kong

RUN chown -R tvb:tvb ./
USER tvb

EXPOSE 80
ENTRYPOINT ["./boot.sh"]

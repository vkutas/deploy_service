FROM tiangolo/uwsgi-nginx-flask:python3.8

ENV LISTEN_PORT 5074
EXPOSE 5074

COPY requirements.txt /app
RUN pip3 install --upgrade pip && pip3 install -r /app/requirements.txt

COPY ./app /app

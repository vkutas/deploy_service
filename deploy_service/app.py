# coding=utf-8
import os
import sys
import json
import logging
import logging.config
import logging.handlers

from flask import Flask
from flask import request, jsonify
import docker
import requests


log = logging.getLogger(__name__)
app = Flask(__name__)
docker_client = docker.from_env()
AUTH_TOKEN = os.getenv('CI_TOKEN', None)  # Берем наш токен из переменной окружения


def init_logging():
    """
    Инициализация логгера
    :return:
    """
    log_format = f"[%(asctime)s] [ CI/CD server ] [%(levelname)s]:%(name)s:%(message)s"
    formatters = {'basic': {'format': log_format}}
    handlers = {'stdout': {'class': 'logging.StreamHandler',
                           'formatter': 'basic'}}
    level = 'INFO'
    handlers_names = ['stdout']
    loggers = {
        '': {
            'level': level,
            'propagate': False,
            'handlers': handlers_names
        },
    }
    logging.basicConfig(level='INFO', format=log_format)
    log_config = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': formatters,
        'handlers': handlers,
        'loggers': loggers
    }
    logging.config.dictConfig(log_config)
    
@app.route('/deploy', methods=['POST'])
def webhook_handler():
    if check_token(request.headers.get('Authorization')):
        if validate_request_format(request):
            log.debug("Update image")
            is_succes = update_container(request.get_json()['owner'], request.get_json()['repository'], request.get_json()['tag'])
            if is_succes:
                return jsonify("{'status': success}"), 200
            else:
                return jsonify("{'status': fail}"), 520
        else:
            return 'Wrong request', 400
    else:
        return 'Authorization required', 401

def check_token(token: str) -> bool:
    if token == AUTH_TOKEN:
        return True
    return False

# TODO
def validate_request_format(request: request):
    return True

def update_container(owner: str, repository_name: str, tag: str) -> bool:
    log.info(f'Starting container update...\nRepository: {owner}\nApplication: {repository_name}\nTag: {tag}')
    image_name = owner + '/' + repository_name
    try:
        log.info(f'Pulling image {image_name}:{tag}')
        docker_client.images.pull(repository=image_name, tag = tag)
    except docker.errors.APIError as api_error:
        log.error(f'Error while pulling the image.\n{api_error}')
        return False
    
    try:
        log.info('Checking application container current status')
        running_instance = docker_client.containers.get(repository_name)
    except docker.errors.NotFound:
        log.info(f"A container '{repository_name} are not running.'")
        running_instance = None
    
    if running_instance is not None:
        log.info('Application container is running. Trying to kill...') 
        running_instance.kill
        log.info('Application container killed.')
        log.info(f'Running containers:\n{docker_client.containers.list()}\n')
        

    log.info('Removing all stoped containers...')
    docker_client.containers.prune()
    log.info('Success')
    log.info(f'Container:\n{docker_client.containers.list(all=True)}\n')

    log.info('Runing new instance...')
    new_instance = docker_client.containers.run(image=image_name + ':' + tag, name=repository_name, detach=True, ports = {'8080': 8080})

    if new_instance is not None:
        log.info('New instance is up and running.')
        return True
    else: 
        log.error('Running a new instance failed')
        return False


def main():
    init_logging()
    if not AUTH_TOKEN:
        log.error('There is no auth token in env')
        sys.exit(1)
    app.run(host='0.0.0.0', port=5074)


if __name__ == '__main__':
    main()

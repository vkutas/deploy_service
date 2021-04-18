# coding=utf-8
import os
import sys
import json
import logging
import logging.config
import logging.handlers

from flask import Flask
from flask import request, jsonify
from flask_expects_json import expects_json
from deploy_service.request_validation import webhook_schema
import docker
import requests
import pkgutil

log = logging.getLogger(__name__)
app = Flask(__name__)
docker_client = docker.from_env()
AUTH_TOKEN = os.getenv('CI_TOKEN', None) 
containers_restart_policy={"Name": "on-failure", "MaximumRetryCount": 3}

search_path = ['.'] # set to None to see all modules importable from sys.path
all_modules = [x[1] for x in pkgutil.iter_modules(path=search_path)]

def init_logging():
    """
    :return:
    """
    log_format = f"[%(asctime)s] [ CD server ] [%(levelname)s]:%(name)s:%(message)s"
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
@expects_json(webhook_schema)
def webhook_handler():
    if check_token(request.headers.get('Authorization')):
        log.debug("Update image")
        is_succes = update_container(**request.get_json())
        if is_succes:
            return jsonify("{'status': success}"), 200
        else:
            return jsonify("{'status': fail}"), 520
    else:
        return jsonify("{'status': 'failure', 'message': 'Authorization required'}"), 401

def check_token(token: str) -> bool:
    if token == AUTH_TOKEN:
        return True
    return False

def update_container(owner: str, repository: str, tag: str, ports: dict) -> bool:
    log.info(f'Starting application update...\nRepository: {owner}\\{repository}\nTag: {tag}')
    image_name = owner + '/' + repository
    ports = {request.get_json().get('ports').get('app_port') : request.get_json().get('ports').get('host_port')}
    try:
        log.info(f"Pulling '{image_name}:{tag}' from docker hub")
        docker_client.images.pull(repository=image_name, tag = tag)
    except docker.errors.APIError as api_error:
        log.error(f'Error while pulling the image.\n{api_error}')
        return False
    
    try:
        log.info(f"Checking '{repository}' container current status")
        running_instance = docker_client.containers.get(repository)
        log.info(f"Running '{repository}' container is found.\n{running_instance}")
    except docker.errors.NotFound:
        log.info(f"A container '{repository} are not running.'")
        running_instance = None
    
    if running_instance is not None:
        log.info('Application container is running. Trying to kill...') 
        running_instance.stop()
        log.info('Application container killed.')
        log.info(f'Running containers:\n{docker_client.containers.list()}\n')
        

    log.info('Removing all stoped containers...')
    docker_client.containers.prune()
    log.info('Success')
    log.info(f'Container:\n{docker_client.containers.list(all=True)}\n')

    log.info('Runing new instance...')

    new_instance = docker_client.containers.run(image=image_name + ':' + tag, name=repository, detach=True, ports = ports, restart_policy=containers_restart_policy)

    if new_instance is not None:
        log.info('New instance is up and running.')
        return True
    else: 
        log.error('Running a new instance failed')
        return False

@app.errorhandler(400)
def bad_request(error):
     return jsonify("{'status': 'failure', 'message': 'Bad Request'}"), 400


def main():
    init_logging()
    if not AUTH_TOKEN:
        log.error('There is no auth token in env')
        sys.exit(1)
    app.run(host='0.0.0.0', port=5074)


if __name__ == '__main__':
    main()

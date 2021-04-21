# Deploy Service

A simple flask application which can pull image from docker hub and run a container on the machine running the application.

## Description

Application is listening port 5074. For now there is only one entry point - `/deploy` which receive the json payload with the following schema:

```json

  "type": "object",
  "properties": {
    "owner": { "type": "string" },
    "repository": { "type": "string" },
    "tag": { "type": "string" },
    "ports": {
      "type": "object",
      "properties": {
        "app_port": { "type": "integer" },
        "host_port": {"type": "integer" }
      },
      "required": [
        "app_port",
        "host_port"
      ]
    }
  },
  "required": [
    "owner",
    "repository",
    "tag",
    "ports"
  ]
}
```

## How to use

0. You need docker, python 3 and pip installed on your system.  

1. Clone the repo and move to the repo directory:  
    ```
    git clone https://github.com/vkutas/deploy_service 
    cd deploy_service 
    ``` 
2. Install application:
    `python3 setup.py install`

3. Copy `deploy_service.service` to the `/etc/systemd/system`
    `cp deploy_service.service /etc/systemd/system`

4. Generate a token and paste it to the `deploy_service.service` file.
    `openssl rand -hex 20`

5. Run the service:
    `sudo systemctl start deploy_service`

To update running container or run new one you can send a request to `http://your_server_address:5074/deploy`.

### Example of request
```json
        {
        "owner": "azvak",
        "repository": "best_app_ever",
        "tag": "1.0.1-release",
        "ports": {
            "app_port": 5823,
            "host_port": 80
            }
        }
```

When application receive such a request it pulls image `azvak/best_app_ever:1.0.1-release` from Docker Hub, stop and remove container with name `best_app_ever` if such container exists and run new one which is based on newly downloaded image.
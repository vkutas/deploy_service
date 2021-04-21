# Deploy Service

A simple flask application which can pull image from docker hub and run a container on the machine running the application.

## Description

Application is listening port 5074, but you can change it in [Dockerfile](Dockerfile). For now there is only one entry point - `/deploy` which receive the json payload with the following schema:

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

**Note:** This build was tested on Ubuntu 20.04 only.

**Note:**  You need [docker](https://docs.docker.com/engine/install/) installed on your system.  

1. Pull the image from docker hub: 

  or clone the repo and build image yourself: 
```
git clone https://github.com/vkutas/deploy_service
cd deploy_service
docker build -t deploy_service:0.0.1 .
```

2. Generate authentication key and save it to the file:   
```
openssl rand -hex 20 > key
```

Run the container:  
```
docker run -d --name dep_test -p 5074:5074 -v /var/run/docker.sock:/var/run/docker.sock -v $(pwd)/key:/app/key  deploy_service:0.0.1
```

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
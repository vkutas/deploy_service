webhook_schema = {
  "type": "object",
  "properties": {
    "owner": {
      "type": "string"
    },
    "repository": {
      "type": "string"
    },
    "tag": {
      "type": "string"
    },
    "ports": {
      "type": "object",
      "properties": {
        "app_port": {
          "type": "integer"
        },
        "host_port": {
          "type": "integer"
        }
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
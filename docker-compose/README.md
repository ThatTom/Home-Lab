# Docker Compose

To aid troubleshooting and diagnostic tasks docker compose files should be construcuted in a uniformed manner, using the below guide as refrence

```
 service-name:
    image: prom/prometheus
    ports:
      - 9090:9090
    deploy:
      replicas: 1
      placement:
        constraints:
          - node.label == xyz
          - node.name == xyz
      restart_policy:
        condition: on-failure
```
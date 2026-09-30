# Docker Compose

## Compose Layout and Standards

To aid troubleshooting and diagnostic tasks docker compose files should be constructed in a uniformed manner, using the below guide as reference

``` YAML
services:
  service-name:
    image: prom/prometheus:v3.5.0
    environment:
      TZ: Europe/London
      SOME_FLAG: "true"
      SOME_SECRET: ${SOME_SECRET}
    ports:
      - "9090:9090"
    volumes:
      - service-data:/data
    networks:
      - diagon-alley
    healthcheck:
      test: ["CMD", "wget", "-qO-", "http://localhost:9090/-/healthy"]
      interval: 30s
      timeout: 5s
      retries: 3
      start_period: 20s
    deploy:
      replicas: 1
      placement:
        constraints:
          - node.hostname == xyz
          - node.labels.xyz == yes
      restart_policy:
        condition: on-failure
      labels:
        # Image update monitoring
        - "diun.enable=true"
        # Traefik
        - "traefik.enable=true"
        - "traefik.swarm.network=diagon-alley"
        # Router
        - "traefik.http.routers.service-name.rule=Host(`service-name.hogwartsnetwork.co.uk`)"
        - "traefik.http.routers.service-name.entrypoints=websecure"
        - "traefik.http.routers.service-name.tls=true"
        - "traefik.http.routers.service-name.tls.certresolver=cloudflare"
        # Service
        - "traefik.http.services.service-name.loadbalancer.server.port=9090"

volumes:
  service-data:
    name: service-data

networks:
  diagon-alley:
    external: true
```

### File layout

- 2 space indentation, with list items indented beneath their key
- Top level sections in the order `services`, `volumes`, `networks`, `secrets`, separated by a single blank line
- A single blank line between each service, and no blank lines within a service
- Named volumes/networks with a body are separated by a blank line, those without are listed together
- `external: false` is the default and is left out

### Service key order

Only the keys a service needs are included, always in the below order

| Order | Keys | Notes |
| --- | --- | --- |
| 1 | `image` | Always first |
| 2 | `container_name`, `hostname`, `init`, `command` | Identity and start up |
| 3 | `runtime`, `read_only`, `security_opt`, `cap_drop`, `cap_add`, `devices`, `tmpfs`, `shm_size` | Runtime and security |
| 4 | `depends_on` | |
| 5 | `env_file`, `environment` | |
| 6 | `ports` | |
| 7 | `volumes`, `secrets` | |
| 8 | `networks` | |
| 9 | `healthcheck` | `test`, `interval`, `timeout`, `retries`, `start_period` |
| 10 | `labels`, `restart` | Only for services run outside of the swarm |
| 11 | `deploy` | `replicas`, `placement`, `restart_policy`, `labels` |

### Formatting

- `environment` uses the map form (`KEY: value`) rather than the list form (`- KEY=value`), with `true`/`false` and other values YAML would otherwise reinterpret (e.g. `"002"`) quoted
- `ports` in the short form are always quoted (`"8080:80"`)
- `labels` use the quoted list form and are grouped under the comments `Image update monitoring`, `Traefik`, `Router` and `Service`, in that order, with any extra groups (middlewares, TCP routers) after
- Swarm services set their labels and restart behaviour under `deploy`; service level `labels` and `restart` are only used by compose files deployed outside of the swarm

All images defined should also have a statically set version rather than using :latest to allow for easier version control, updating and pre-release testing

Where possible individual services should be combined into a stack instead of using separate compose files for each

## Update Deployment

1. New version made available for a service that is in service
2. Review updates purpose

- If the update is purely feature based refer to standard release
- If the update is security based/addresses an urgent issue refer to urgent release
- If the update is a development build being used in a non production service then refer to development release

#### Urgent Release

1. Check current version configured within the .env for the service/stack
2. Check new version that is available
3. Update the service/stack .env with the updated version
4. Manually perform a service/stack deployment
5. Verify that the service has been deployed as expected
6. Ensure all other services that depend on the service are also operating as expected

*If services fail to restore, check logs for any clear issues; if not immediately resolvable, change the version back to the previous version and redeploy the stack/service immediately*

#### Standard Release

1. Check current version configured within the .env for the service/stack
2. Check new version that is available
3. Await 1 week post release and check for any reported bugs or issues
4. If no service breaking bugs/issues are found then update the service/stack .env with the updated version
5. Configure the container update procedure with the relevant stack/service and configure the run time to be 2AM of the next morning
6. Following the completion of the procedure verify the service has restored/successfully update the next morning
7. Ensure all other services that depend on the service are also operating as expected

*If services fail to restore, check logs for any clear issues; if not immediately resolvable, change the version back to the previous version and redeploy the stack/service immediately*

#### Development Release

1. Check current version configured within the .env for the service/stack
2. Check new version that is available
3. Update the service/stack .env with the updated version
4. Manually perform a service/stack deployment
5. Verify that the service has been deployed as expected
# Docker Compose

## Compose Layout and Standards

To aid troubleshooting and diagnostic tasks docker compose files should be constructed in a uniformed manner, using the below guide as reference

``` YAML
services:
  service-name:
    image: prom/prometheus:v3.5.0
    environment:
      TZ: UTC
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
- Top level sections in the order `services`, `volumes`, `networks`, `configs`, `secrets`, separated by a single blank line
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
| 7 | `volumes`, `configs`, `secrets` | |
| 8 | `networks` | |
| 9 | `healthcheck` | `test`, `interval`, `timeout`, `retries`, `start_period` |
| 10 | `labels`, `restart` | Only for services run outside of the swarm |
| 11 | `deploy` | `replicas`, `placement`, `restart_policy`, `labels` |

### Formatting

- `environment` uses the map form (`KEY: value`) rather than the list form (`- KEY=value`), with `true`/`false` and other values YAML would otherwise reinterpret (e.g. `"002"`) quoted
- `ports` in the short form are always quoted (`"8080:80"`)
- `labels` use the quoted list form and are grouped under the comments `Traefik`, `Router` and `Service`, in that order, with any extra groups (middlewares, TCP routers) after
- Swarm services set their labels and restart behaviour under `deploy`; service level `labels` and `restart` are only used by compose files deployed outside of the swarm

All images defined should also have a statically set version rather than using :latest to allow for easier version control, updating and pre-release testing

Every long running service has a `healthcheck` so Swarm restarts it when it stops responding, not only when it exits. Leave it out when the image already defines one (`docker buildx imagetools inspect --format "{{json .Image.config.Healthcheck}}" <image>`), and check the image has the tool the test uses, many have `wget` or `curl` but not both

Where possible individual services should be combined into a stack instead of using separate compose files for each

## Update Deployment

Image versions are pinned in the compose files, and [Renovate](/renovate.json) opens a pull request in Gitea for each new version once it's at least 7 days old. The compose file in `main` is the record of what should be running, and the [changelog](/hosted-services/CHANGELOG.md) is regenerated from it daily at 12:00 UTC.

### Standard update

1. Read the release notes linked in the Renovate pull request, looking for breaking changes, required migrations or new required settings
2. Updates labelled `careful` (Immich, Vaultwarden) or `major` need extra care: check the upstream upgrade guide and that last night's backup succeeded first
3. Merge the pull request
4. Deploy the stack from `main`
5. Check the service: `docker service ps <stack>_<service>` shows it running (and healthy, where it has a healthcheck), the site loads, and anything that depends on it still works

### Urgent update

For security fixes or a bug affecting a running service, when waiting for Renovate isn't an option:

1. Change the image tag in the compose file on `main` (or merge Renovate's pull request early from the dependency dashboard)
2. Deploy and check it as in a standard update

### Our own images

Images built from our own repositories (Odd Jobs, Nemoir, MeshHub, Spindle) are tagged by their build workflows and bumped here by hand. Check the new tag was built for every architecture its service can run on: the Raspberry Pis are `arm64` and the Lenovos `amd64`.

```
docker buildx imagetools inspect <image>:<tag>
```

### Rolling back

If a service doesn't come back after an update and the logs (`docker service logs <stack>_<service>`) don't show an obvious fix, revert the commit and redeploy straight away:

```
git revert <commit>
```

`docker service rollback <stack>_<service>` is quicker in an emergency, but the next deploy puts the new version back unless the commit is reverted too.

An update that migrated a database may not run against the older version again. In that case restore the service's data from the backup taken before the update (see [Restoring a Single Service](/disaster-recovery/README.md#restoring-a-single-service)).

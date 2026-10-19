# Changelog

## Live Services

Generated from the image versions in the [docker compose files](/docker-compose/) by [generate-changelog.sh](/.gitea/scripts/generate-changelog.sh), don't edit by hand. Each version change is in the git history of its compose file.

| Stack | Service | Category | Image | Version |
| --- | --- | --- | --- | --- |
| [ollama](/docker-compose/ai/ollama.yaml) | ollama | ai | `ollama/ollama` | 0.35.0 |
| [openwebui](/docker-compose/ai/openwebui.yaml) | open-webui | ai | `ghcr.io/open-webui/open-webui` | v0.12.3 |
| [gitea-mirror](/docker-compose/git/gitea-mirror.yaml) | gitea-mirror | git | `ghcr.io/raylabshq/gitea-mirror` | v3.41.0 |
| [gitea-runner](/docker-compose/git/gitea-runner.yaml) | gitea-runner-pi | git | `gitea/runner` | 4.1.0 |
| [gitea-runner](/docker-compose/git/gitea-runner.yaml) | gitea-runner-lenovo | git | `gitea/runner` | 4.1.0 |
| [gitea](/docker-compose/git/gitea.yaml) | server | git | `gitea/gitea` | 1.27 |
| [core](/docker-compose/komodo/core.yaml) | postgres | komodo | `ghcr.io/ferretdb/postgres-documentdb` | latest (untagged) |
| [core](/docker-compose/komodo/core.yaml) | ferretdb | komodo | `ghcr.io/ferretdb/ferretdb` | latest (untagged) |
| [core](/docker-compose/komodo/core.yaml) | core | komodo | `ghcr.io/moghtech/komodo-core` | 2 (or `COMPOSE_KOMODO_IMAGE_TAG`) |
| [periphery](/docker-compose/komodo/periphery.yaml) | periphery | komodo | `ghcr.io/moghtech/komodo-periphery` | 2 (or `COMPOSE_KOMODO_IMAGE_TAG`) |
| [jellyfin](/docker-compose/media/consume/jellyfin.yaml) | jellyfin | media/consume | `ghcr.io/jellyfin/jellyfin` | 10.11.11 |
| [radarr](/docker-compose/media/management/radarr.yaml) | radarr | media/management | `ghcr.io/hotio/radarr` | release-6.3.0.10514 |
| [seerr](/docker-compose/media/management/seerr.yaml) | seerr | media/management | `ghcr.io/seerr-team/seerr` | v3.5.0 |
| [sonarr](/docker-compose/media/management/sonarr.yaml) | sonarr | media/management | `ghcr.io/hotio/sonarr` | release-4.0.19.2979 |
| [spindle](/docker-compose/media/management/spindle.yaml) | spindle | media/management | `ghcr.io/thattom/spindle` | 2804e1f |
| [grafana](/docker-compose/monitoring/grafana.yaml) | grafana | monitoring | `grafana/grafana-enterprise` | 13.2.3 |
| [loki](/docker-compose/monitoring/loki.yaml) | loki | monitoring | `grafana/loki` | 3.7.8 |
| [loki](/docker-compose/monitoring/loki.yaml) | alloy | monitoring | `grafana/alloy` | v1.20.1 |
| [prometheus](/docker-compose/monitoring/prometheus.yaml) | prometheus | monitoring | `prom/prometheus` | v3.15.0 |
| [prometheus](/docker-compose/monitoring/prometheus.yaml) | alertmanager | monitoring | `prom/alertmanager` | v0.34.1 |
| [prometheus](/docker-compose/monitoring/prometheus.yaml) | blackbox-exporter | monitoring | `prom/blackbox-exporter` | v0.29.0 |
| [prometheus](/docker-compose/monitoring/prometheus.yaml) | node-exporter | monitoring | `prom/node-exporter` | v1.12.1 |
| [prometheus](/docker-compose/monitoring/prometheus.yaml) | cadvisor | monitoring | `ghcr.io/google/cadvisor` | v0.60.6 |
| [ntfy](/docker-compose/network-services/ntfy.yaml) | ntfy | network-services | `binwiederhier/ntfy` | v2.29.0 |
| [socket-proxy](/docker-compose/network-services/socket-proxy.yaml) | socket-proxy | network-services | `tecnativa/docker-socket-proxy` | latest |
| [termix](/docker-compose/network-services/termix.yaml) | termix | network-services | `ghcr.io/lukegus/termix` | 26.10.2 |
| [traefik](/docker-compose/network-services/traefik.yaml) | traefik | network-services | `traefik` | v3.7 |
| [voidauth](/docker-compose/network-services/voidauth.yaml) | voidauth | network-services | `voidauth/voidauth` | 1.16.0 |
| [wireguard](/docker-compose/network-services/wireguard.yaml) | wgdashboard | network-services | `ghcr.io/wgdashboard/wgdashboard` | v4.3.3 |
| [homepage](/docker-compose/single-services/homepage.yaml) | homepage | single-services | `ghcr.io/gethomepage/homepage` | v2.6.0 |
| [immich](/docker-compose/single-services/immich.yaml) | immich-server | single-services | `ghcr.io/immich-app/immich-server` | v3.3.3 |
| [immich](/docker-compose/single-services/immich.yaml) | immich-machine-learning | single-services | `ghcr.io/immich-app/immich-machine-learning` | v3.3.3 |
| [immich](/docker-compose/single-services/immich.yaml) | redis | single-services | `docker.io/valkey/valkey` | 9 + digest |
| [immich](/docker-compose/single-services/immich.yaml) | database | single-services | `ghcr.io/immich-app/postgres` | 14-vectorchord0.4.3-pgvectors0.2.0 + digest |
| [leafwiki](/docker-compose/single-services/leafwiki.yaml) | leafwiki | single-services | `ghcr.io/perber/leafwiki` | v0.14.1 |
| [meshhub](/docker-compose/single-services/meshhub.yaml) | meshhub | single-services | `git.hogwartsnetwork.co.uk/hogwartsimages/meshhub` | latest (or `MESHHUB_TAG`) |
| [nemoir](/docker-compose/single-services/nemoir.yaml) | nemoir | single-services | `git.hogwartsnetwork.co.uk/hogwartsimages/nemoir` | sha-5944619 |
| [oddjobs](/docker-compose/single-services/oddjobs.yaml) | odd-jobs | single-services | `git.hogwartsnetwork.co.uk/hogwartsimages/odd-jobs` | 19.10.26 |
| [paperless](/docker-compose/single-services/paperless.yaml) | broker | single-services | `docker.io/valkey/valkey` | 9-alpine |
| [paperless](/docker-compose/single-services/paperless.yaml) | webserver | single-services | `ghcr.io/paperless-ngx/paperless-ngx` | 3.3.2 |
| [paperless](/docker-compose/single-services/paperless.yaml) | gotenberg | single-services | `docker.io/gotenberg/gotenberg` | 8.37 |
| [paperless](/docker-compose/single-services/paperless.yaml) | tika | single-services | `docker.io/apache/tika` | 3.3.1.0 |
| [rackpad](/docker-compose/single-services/rackpad.yaml) | rackpad | single-services | `ghcr.io/kobii-git/rackpad` | 1.8.3 |
| [semaphore](/docker-compose/single-services/semaphore.yaml) | semaphore | single-services | `semaphoreui/semaphore` | v2.19.16 |
| [spoolman](/docker-compose/single-services/spoolman.yaml) | spoolman | single-services | `ghcr.io/donkie/spoolman` | 0.27.0 |
| [tankbook](/docker-compose/single-services/tankbook.yaml) | db | single-services | `postgres` | 16-alpine |
| [tankbook](/docker-compose/single-services/tankbook.yaml) | app | single-services | `ghcr.io/tankbook/tankbook-app` | 1.0.1 |
| [trek](/docker-compose/single-services/trek.yaml) | app | single-services | `mauriceboe/trek` | 4.3.3 |
| [vaultwarden](/docker-compose/single-services/vaultwarden.yaml) | vaultwarden | single-services | `vaultwarden/server` | 1.37.4 |

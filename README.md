# Hogwarts Homelab

Self hosted debian based home lab running a Docker Swarm cluster for high availability and ease of management/disaster recovery

## [Hosted Services](/hosted-services/)

Hosted services within the Hogwarts Network/Homelab, changelog version tracking and required documentation hosting

- [Changelog](/hosted-services/CHANGELOG.md) - currently live services and their versions

## Hardware

| Node | Hardware | Notes |
| --- | --- | --- |
| dumbledore | Raspberry Pi 4B+ | PoE Hat for power and basic cooling |
| flitwick | Raspberry Pi 4B+ | PoE Hat for power and basic cooling |
| dobby | Lenovo Micro PC | |
| winky | Lenovo Micro PC | |

## [Network](/network/)

Split into VLANs on `10.10.0.0/16`, where the third octet matches the VLAN ID

- 10 Management, 20 Servers, 30 Trusted, 40 IoT, 50 Media, 60 Guest, 70 Ceph (not routed), 80 Work
- 99 WireGuard for remote access

## [Disaster Recovery](/disaster-recovery/)

Backup model (daily Rustic snapshots to Backblaze B2), the break-glass kit and the steps to rebuild a failed node

## [Docker Compose](/docker-compose/)

Files used for the deployment of services within the docker swarm cluster, grouped by purpose

| Folder | Contents |
| --- | --- |
| [ai](/docker-compose/ai/) | Ollama and Open WebUI |
| [git](/docker-compose/git/) | Gitea and the Gitea Actions runner |
| [komodo](/docker-compose/komodo/) | Komodo Core and Periphery for container management |
| [media](/docker-compose/media/) | Jellyfin (`consume`) and the Radarr/Sonarr/Seerr/Spindle stack (`management`) |
| [monitoring](/docker-compose/monitoring/) | Grafana and Prometheus |
| [network-services](/docker-compose/network-services/) | Traefik, VoidAuth, ntfy, Termix, WGDashboard and static Traefik routes |
| [single-services](/docker-compose/single-services/) | Standalone applications such as Vaultwarden, Immich and Paperless-ngx |

All compose files follow the layout and standards in the [Docker Compose README](/docker-compose/README.md), including pinned image versions rather than `latest`

## Updates

Image updates are managed by [Renovate](/renovate.json), which runs daily at 03:00 UTC through a [Gitea Actions workflow](/.gitea/workflows/renovate.yaml) and opens a pull request for each new image version

- Releases must be at least 7 days old before a pull request is raised
- Major version updates require approval on the dependency dashboard first
- Immich and Vaultwarden updates are labelled `careful`

Updates are then deployed following the release process in the [Docker Compose README](/docker-compose/README.md#update-deployment)

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

## Email

Outgoing email from services is sent through [Purelymail](https://purelymail.com), the email provider for the Hogwarts Network

| Setting | Value |
| --- | --- |
| SMTP host | `smtp.purelymail.com` |
| Port / security | `465` with SSL/TLS, or `587` with STARTTLS for services that only support that |
| Username | The full email address |
| Password | The account password, or an app password if the account has two factor authentication |

The login is held in the Komodo Variables `SMTP_USERNAME` and `SMTP_PASSWORD`, shared by every stack that sends email (currently Joplin)

## [3D Models](/3d-models/)

Printable parts for the 10 inch rack the nodes sit in, and the mounts for the kit inside it

## [Network](/network/)

Split into VLANs on `10.10.0.0/16`, where the third octet matches the VLAN ID

- 10 Management, 20 Servers, 30 Trusted, 40 IoT, 50 Media, 60 Guest, 70 Ceph (not routed), 80 Work
- 99 WireGuard for remote access

## [Ansible](/ansible/)

Playbooks run from Semaphore that set up the nodes (users, Docker, OS updates, backups, the Traefik floating IP) and the Swarm networks, labels, secrets and NFS volumes the stacks rely on, and read, back up and manage the router and switches

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
| [monitoring](/docker-compose/monitoring/) | Grafana, Prometheus and Loki |
| [network-services](/docker-compose/network-services/) | Traefik, VoidAuth, ntfy, Termix, WGDashboard and static Traefik routes |
| [single-services](/docker-compose/single-services/) | Standalone applications such as Vaultwarden, Immich and Paperless-ngx |

All compose files follow the layout and standards in the [Docker Compose README](/docker-compose/README.md), including pinned image versions rather than `latest`

## [Komodo Resources](/komodo-resources/)

Komodo resource definitions in TOML, such as the [2AM - Auto Update](/komodo-resources/auto-update.toml) procedure that re-clones the repos and deploys any stacks that changed on `main`

## Updates

Image updates are managed by [Renovate](/renovate.json), which runs daily at 03:00 UTC through a [Gitea Actions workflow](/.gitea/workflows/renovate.yaml) and opens a pull request for each new image version

- Releases must be at least 7 days old before a pull request is raised
- Major version updates require approval on the dependency dashboard first
- Immich and Vaultwarden updates are labelled `careful`

Updates are then deployed following the release process in the [Docker Compose README](/docker-compose/README.md#update-deployment). The [changelog](/hosted-services/CHANGELOG.md) of live versions is regenerated from the compose files by a [Gitea Actions workflow](/.gitea/workflows/changelog.yaml) on every push to `main`

# Disaster Recovery

How the homelab is backed up, what you need to hand before anything goes wrong, and how to rebuild a single failed node.

## Backup Model

Everything needed to rebuild the lab falls into one of three places:

| What | Where it lives | How it comes back |
| --- | --- | --- |
| Node setup (users, SSH, keepalived, backups, Swarm networks, labels and NFS volumes) | Ansible in this repo | Re-run the playbooks |
| Service definitions and their config files | Compose files and Swarm configs in this repo | Redeploy the stacks |
| Service data (Docker volumes, databases) | Rustic snapshots in Backblaze B2 | Restore from the snapshot |

### Rustic backups

Set up by [ansible/backups.yml](/ansible/backups.yml) and the [rustic role](/ansible/roles/rustic/).

- **Schedule** - every node backs up daily at 02:00, plus up to 15 minutes of random delay
- **Destination** - one shared, encrypted Rustic repository in a Backblaze B2 bucket. Every snapshot records the hostname it came from, so each node's backups can be picked out with `--filter-host <node>`
- **Retention** - 7 daily, 4 weekly and 6 monthly snapshots per node. dumbledore prunes the repository every Sunday at 05:00
- **Included**
  - `/var/lib/docker/volumes` on the node's local disk
  - `/var/backups/rustic`, written just before each backup:
    - `postgres/<stack>_<service>.sql.gz` - `pg_dumpall` of every running Postgres container (Komodo, Immich, Tankbook)
    - `sqlite/<volume path>` - a consistent copy of every SQLite database in the volumes
- **Excluded**
  - Raw Postgres data directories (the dumps replace them)
  - Cache volumes (`*cache*`) and Semaphore's temp volume
  - Loki's log storage (`loki-data`), logs start again from empty after a restore
  - NFS volumes (media, Termix), which live on gringotts

### Not covered by these backups

| Item | Where it is | Risk |
| --- | --- | --- |
| Media and Termix data | gringotts NFS shares | Needs the NAS's own backup/redundancy |
| Komodo `core.env` / `periphery.env` | `~/komodo` on dumbledore | Not backed up, keep a copy in the break-glass kit |
| Komodo backups path (`COMPOSE_KOMODO_BACKUPS_PATH`) | Host folder on dumbledore | Not backed up |
| Stack `.env` files (Nemoir, Paperless, Rackpad) | Wherever the stacks are deployed from | Keep copies, or move the values into Komodo |
| Paperless export / consume folders | `/home/tomt/export`, `/mnt/consume` on dobby | Not backed up |
| Router and switch configs | leaky-cauldron, floo, portkey | Export them after every change |
| Non-Swarm services (Ollama, WGDashboard, meshhub) | Their own hosts | Volumes are only covered if the host runs the Rustic role |
| Traefik certificates | `traefik-letsencrypt` volume on each manager | Not needed, re-issued automatically |

## Break-Glass Kit

Keep these **outside the lab** (e.g. a password manager not hosted on it, plus an offline copy). Vaultwarden, Gitea and Semaphore all run on the nodes being recovered, so none of them can be relied on during a recovery.

- [ ] `rustic_password` - without it the backups cannot be decrypted
- [ ] B2 `b2_key_id`, `b2_key`, `b2_bucket`, `b2_bucket_id`
- [ ] The **ansible** SSH private key (its public half is in [ssh-keys/ansible](/ansible/roles/base/files/ssh-keys/ansible/))
- [ ] Your own **tomt** SSH private key
- [ ] The password used for the **harry** bootstrap user
- [ ] Komodo `core.env` and `periphery.env`, and the stack `.env` files
- [ ] A recent clone of this repository (Gitea runs on dobby)
- [ ] Router and switch config exports

## Which Services Run Where

Services pinned to a node only come back once that node's data is restored.

| Node | Role | Pinned services |
| --- | --- | --- |
| dumbledore | Swarm manager, Traefik VIP holder, Rustic prune | Komodo Core (Postgres, FerretDB), VoidAuth (SSO), ntfy, Leafwiki, Rackpad, Tankbook |
| flitwick | Swarm manager, Traefik backup | Nemoir, Open WebUI (`ai` label) |
| dobby | Worker | Gitea, Gitea Mirror, Immich, Paperless, Vaultwarden, Grafana, Prometheus, Alertmanager, Loki, TREK |
| winky | Worker | Semaphore, Spoolman, Odd Jobs |
| dobby / winky | `media` label | Jellyfin, Radarr, Sonarr, Seerr, Spindle (whichever node they were last on) |
| Any | | Traefik (managers), Homepage, Termix, blackbox_exporter, Gitea runners, node_exporter, cAdvisor, Alloy, Komodo Periphery, socket-proxy |

Knock-on effects to plan for:

- **dumbledore down** - SSO (VoidAuth) and Komodo are unavailable, so log in with local accounts where services have them
- **dobby down** - Gitea is unavailable, so Semaphore and Komodo cannot pull the repo. Use your local clone (see [Running Ansible Without Semaphore](#running-ansible-without-semaphore)). Prometheus and Alertmanager also run there, so no alerts are sent while it is down
- **winky down** - Semaphore is unavailable, run Ansible from another machine

## Recovering a Single Node

These steps rebuild a failed node on new or wiped hardware, keeping its hostname and IP, and restore its data from the last backup. Replace `<node>` with the node's name and `<ip>` with its address from the [network README](/network/README.md).

### 1. Prepare the cluster

From a working manager:

```
docker node ls
```

**If the failed node was a worker** (dobby, winky):

```
docker node rm --force <node>
```

**If the failed node was a manager** (dumbledore, flitwick): with only two managers the survivor has lost quorum, so running services keep going but nothing can be changed or rescheduled. On the surviving manager:

```
docker swarm init --force-new-cluster --advertise-addr <survivor ip>
docker node rm --force <node>
```

The keepalived VIP (`10.10.20.2`) moves to the surviving manager on its own as long as its Traefik is healthy.

### 2. Rebuild the operating system

1. Install the same OS the node had (Raspberry Pi OS / Ubuntu Server)
2. Set the hostname to `<node>` and the static address to `<ip>` (VLAN 20)
3. Create the bootstrap user **harry** with sudo rights and the break-glass password
4. Install Docker Engine
5. On Ubuntu 25.10+, check `/usr/bin/sudo.ws` exists (`sudo apt install sudo` if not), Ansible uses it on the workers

### 3. Bootstrap with Ansible

Run the **bootstrap** template in Semaphore (or [without Semaphore](#running-ansible-without-semaphore)). It logs in as harry, creates the `tomt` and `ansible` accounts with their keys, turns off password SSH, then disables harry.

The node's SSH host key has changed, so if Semaphore refuses to connect, clear the old entry from Semaphore's known hosts or run it once more (it uses `accept-new`).

### 4. Rejoin the swarm, drained

On a manager, get the join command:

```
docker swarm join-token worker     # or: docker swarm join-token manager
```

Run the printed `docker swarm join ...` on the rebuilt node, then **immediately drain it** from a manager so its pinned services don't start with empty volumes:

```
docker node update --availability drain <node>
```

### 5. Re-apply node configuration

Run these templates (or `site.yml`, which runs them all):

1. `swarm.yml` - node labels and NFS volumes
2. `traefik-config.yml` and `keepalived.yml` - managers only
3. `backups.yml` - installs Rustic and its config, needed for the restore

### 6. Restore the volumes

On the rebuilt node, as root (`sudo -i`):

```
# Find the latest snapshot from this node and note its ID
rustic snapshots --filter-host <node>

# Docker must be stopped so it picks up the restored volumes when it starts
systemctl stop docker docker.socket

rustic restore <snapshot-id>:/var/lib/docker/volumes /var/lib/docker/volumes
rustic restore <snapshot-id>:/var/backups/rustic /var/backups/rustic

systemctl start docker
```

Then put the consistent SQLite copies over the restored database files:

```
cd /var/backups/rustic/sqlite
find . -type f | while read -r db; do
    cp -a "$db" "/var/lib/docker/volumes/${db#./}"
    rm -f "/var/lib/docker/volumes/${db#./}-wal" "/var/lib/docker/volumes/${db#./}-shm"
done
```

### 7. Restore the Postgres databases

Only needed on nodes running Postgres (dumbledore: Komodo, Tankbook; dobby: Immich). The raw database folders aren't in the backup, so each database starts empty and is loaded from its dump **before** its app is allowed to start.

From a manager, scale the app down first, then make the node active so only the database starts on it:

```
docker service scale <app service>=0          # e.g. tankbook_app, immich_immich-server, komodo_core
docker node update --availability active <node>
```

On the node, load the dump into the database container:

```
c=$(docker ps -q --filter name=<stack>_<db service>)       # e.g. tankbook_db
gunzip -c /var/backups/rustic/postgres/<stack>_<db service>.sql.gz \
  | docker exec -i "$c" psql -U <postgres user> -d postgres
```

Errors about the current user's role already existing or being in use are expected, the rest of the dump still loads.

**Immich** needs its search path fixed while loading, as in Immich's own restore guide:

```
gunzip -c /var/backups/rustic/postgres/immich_database.sql.gz \
  | sed "s/SELECT pg_catalog.set_config('search_path', '', false);/SELECT pg_catalog.set_config('search_path', 'public, pg_catalog', true);/g" \
  | docker exec -i "$c" psql -U postgres -d postgres
```

Then scale the app back up:

```
docker service scale <app service>=1
```

### 8. Bring the node back into service

From a manager:

```
docker node update --availability active <node>
docker node ls
docker service ls      # every service should show its full replica count
```

If it was a manager and you rebuilt the cluster in step 1, re-add it as a manager with the `join-token manager` command (step 4).

### 9. Verify

- [ ] Each pinned service from the [table above](#which-services-run-where) loads and has its data
- [ ] Managers: `curl http://127.0.0.1:8082/ping` returns `OK`, and only one manager holds `10.10.20.2`
- [ ] Homepage shows the node and its services as up
- [ ] Start a backup by hand and check it succeeds: `systemctl start rustic-backup.service`, then `journalctl -u rustic-backup -n 50`

## Running Ansible Without Semaphore

For when winky (Semaphore) or dobby (Gitea) is down. From any Linux machine (or WSL) that can reach the nodes:

```
pipx install ansible-core
git clone <your local copy or a backup of this repo> homelab && cd homelab/ansible
ansible-galaxy collection install -r collections/requirements.yml

# The same secrets Semaphore normally provides as environment variables
export harry_password='...' rustic_password='...' b2_key_id='...' b2_key='...' b2_bucket='...' b2_bucket_id='...'

ansible-playbook -i inventory/homelab.yml --private-key ~/.ssh/ansible_key bootstrap.yml
```

Swap `bootstrap.yml` for any other playbook, and add `--limit <node>` to run against one node only.

## Restoring a Single Service

The same idea on a smaller scale, for when one service's data is lost or corrupted rather than a whole node:

```
docker service scale <service>=0
rustic snapshots --filter-host <node>
rustic restore <snapshot-id>:/var/lib/docker/volumes/<volume> /var/lib/docker/volumes/<volume>
docker service scale <service>=1
```

For a SQLite or Postgres service, use the dump from `/var/backups/rustic` as in steps 6 and 7.

## Testing

A backup that has never been restored is not proven. Every few months:

- [ ] Restore one service's volume to a spare path (`rustic restore <id>:/var/lib/docker/volumes/<volume> /tmp/restore-test`) and check the files
- [ ] Load one Postgres dump into a throwaway `postgres` container
- [ ] Check the break-glass kit is complete and its secrets still work

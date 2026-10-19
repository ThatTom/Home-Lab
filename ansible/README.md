# Ansible

Playbooks that set up the nodes and the Swarm resources the stacks rely on. Everything that isn't a container lives here: users and SSH, Docker itself, OS updates, backups, the Traefik floating IP, and the networks, labels, secrets and NFS volumes the compose files expect to already exist.

## Running the Playbooks

The playbooks are run from **Semaphore**, which clones this repo and logs in to the nodes as the `ansible` user with its SSH key. Each playbook has a template there, using the inventory [inventory/homelab.yml](/ansible/inventory/homelab.yml).

When Semaphore is down, run them from any Linux machine (or WSL) instead, see [Running Ansible Without Semaphore](/disaster-recovery/README.md#running-ansible-without-semaphore).

The collections they need are in [collections/requirements.yml](/ansible/collections/requirements.yml), which Semaphore installs before every run.

### Secrets

Secrets are never stored in the repo. They're read from environment variables, which Semaphore provides from **environment secrets** in the template's Variable Group (extra variable secrets don't reach the lookups). [group_vars/all.yml](/ansible/inventory/group_vars/all.yml) shows which variable each one comes from.

| Variable | Used by | For |
| --- | --- | --- |
| `harry_password` | bootstrap.yml | The bootstrap user's password, only needed on a fresh node |
| `rustic_password` | backups.yml | The Rustic repository password |
| `b2_key_id`, `b2_key`, `b2_bucket`, `b2_bucket_id` | backups.yml | The Backblaze B2 bucket the backups go to |
| `ntfy_alert_token` | swarm.yml | Swarm secret Alertmanager posts alerts to ntfy with |
| `healthchecks_ping_url` | swarm.yml | Swarm secret Alertmanager sends its Watchdog heartbeat to |

## Inventory

| Group | Hosts | Gets |
| --- | --- | --- |
| `swarm_managers` | dumbledore, flitwick | Traefik's dynamic config and the keepalived VIP (`10.10.20.2`), on top of everything else |
| `swarm_workers` | dobby, winky | Ubuntu nodes, which use `sudo.ws` because Ansible doesn't recognise sudo-rs's password prompt |
| `swarm` / `all` | All four nodes | |

winky is also a Swarm manager, so the cluster keeps quorum with any one manager down, but it stays out of `swarm_managers` since it doesn't run Traefik or hold the VIP.

Other settings in the inventory:

- **Node labels** (`swarm_node_labels`, [homelab.yml](/ansible/inventory/homelab.yml)) - `traefik` on the nodes that run Traefik, `ai` for Open WebUI and `media` for the media stack
- **Overlay networks**, **Swarm secrets** and **NFS volumes** ([group_vars/all.yml](/ansible/inventory/group_vars/all.yml)). An NFS volume marked `create: true` has its folder made on the NAS first, owned by `owner` if it's set, which needs the share's Maproot User to be root
- **Users** (`managed_users`), with their public keys in [roles/base/files/ssh-keys](/ansible/roles/base/files/ssh-keys/)

## Playbooks

| Playbook | Runs on | What it does | When |
| --- | --- | --- | --- |
| [site.yml](/ansible/site.yml) | All | Everything below except patch.yml, in order | Rebuilding a node, or to check every node matches the repo |
| [bootstrap.yml](/ansible/bootstrap.yml) | All | Creates the `tomt` and `ansible` users and their keys, turns off password SSH, keeps time sync running and caps the journal size, then disables the `harry` bootstrap user | New nodes, and after changing users, keys or the base role |
| [docker.yml](/ansible/docker.yml) | All, one at a time | Installs Docker on nodes without it, merges log rotation into `daemon.json` and sets up a weekly prune of old images, build cache and stopped containers | New nodes, and after changing the Docker settings |
| [updates.yml](/ansible/updates.yml) | All | Daily unattended security updates (never rebooting or upgrading Docker) and the reboot-required metric | New nodes |
| [swarm.yml](/ansible/swarm.yml) | Managers, then all | Overlay networks, node labels, Swarm secrets, and the NFS volumes on every node | After changing any of those in the inventory |
| [traefik-config.yml](/ansible/traefik-config.yml) | swarm_managers | Copies the static Traefik routes in [network/traefik-configs](/network/traefik-configs/) to each Traefik node | Automatically, see below |
| [keepalived.yml](/ansible/keepalived.yml) | swarm_managers | The floating IP that follows a healthy Traefik, and checks exactly one node holds it | After changing the VIP or priorities |
| [backups.yml](/ansible/backups.yml) | All | Rustic, its B2 config, the database dump script and the daily backup timer | New nodes, and after changing what's backed up |
| [restore-test.yml](/ansible/restore-test.yml) | dumbledore | The monthly restore test timer. Add `-e restore_test_run_now=true` to run it straight away | After changing the restore test |
| [patch.yml](/ansible/patch.yml) | Workers, then managers, one at a time | Rolling OS updates, see below | On a schedule in Semaphore |

### Automatic runs

A [Gitea Actions workflow](/.gitea/workflows/traefik-config.yaml) runs the traefik-config template in Semaphore whenever a push to `main` changes `network/traefik-configs/`, the playbook or its role, and fails if the Semaphore run does.

### Rolling updates (patch.yml)

Each node in turn is checked against the rest of the cluster, drained, upgraded, rebooted if it needs it, and made active again once the Swarm sees it as ready. The run stops at the first failure and leaves that node drained to look at. Services pinned to a node are down while it's drained.

Draining the node Semaphore is running on would stop the run halfway, so that node is skipped. Drain it by hand first so Semaphore moves elsewhere, or run the playbook from another machine with `-e os_patch_skip_controller=false`. docker.yml does the same and skips restarting Docker on Semaphore's node, pass `-e docker_skip_controller=false` to restart it from another machine.

## Roles

| Role | Used by | Notes |
| --- | --- | --- |
| [base](/ansible/roles/base/) | bootstrap.yml | Users, SSH keys, sudo, sshd settings, time sync and the journal size limit. Refuses to run if a user has no public key, to avoid a lockout |
| [retire_users](/ansible/roles/retire_users/) | bootstrap.yml | Disables the bootstrap user once the `ansible` login is proven to work |
| [docker_engine](/ansible/roles/docker_engine/) | docker.yml | Docker install, `daemon.json` settings (merged, so settings added by hand are kept) and the prune timer |
| [updates](/ansible/roles/updates/) | updates.yml, patch.yml | unattended-upgrades and the `node_reboot_required` metric |
| [os_patch](/ansible/roles/os_patch/) | patch.yml | Drain, upgrade, reboot and return a node to service |
| [swarm_cluster](/ansible/roles/swarm_cluster/) | swarm.yml | Networks, node labels and Swarm secrets, from one manager |
| [docker_nfs_volumes](/ansible/roles/docker_nfs_volumes/) | swarm.yml | NFS-backed Docker volumes on every node. Changing a volume's path recreates it, which fails while any container (even a stopped one) uses it |
| [traefik_dynamic](/ansible/roles/traefik_dynamic/) | traefik-config.yml | Copies the static routes to `/opt/traefik/dynamic`, which Traefik watches |
| [keepalived](/ansible/roles/keepalived/) | keepalived.yml | VRRP for the Traefik VIP, following Traefik's ping on each node |
| [rustic](/ansible/roles/rustic/) | backups.yml | Backups to B2, see the [Disaster Recovery README](/disaster-recovery/README.md#backup-model) |
| [restore_test](/ansible/roles/restore_test/) | restore-test.yml | Restores each node's latest database dumps and checks they're usable |

## Metrics and Alerts

Several roles write results to node_exporter's textfile directory (`/var/lib/node_exporter/textfile`), which Prometheus alerts on ([alert-rules.yml](/docker-compose/monitoring/configs/alert-rules.yml)):

| Metric | Written by | Alerts |
| --- | --- | --- |
| `rustic_*` | rustic | BackupOverdue, BackupFailed, BackupNeverReported, PruneOverdue, PruneFailed |
| `node_reboot_required*` | updates | RebootRequired, after 8 days |
| `restore_test_*` | restore_test | RestoreTestFailed, RestoreTestOverdue |

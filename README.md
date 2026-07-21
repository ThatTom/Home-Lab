# Hogwarts Homelab

Self hosted debian based home lab runing a Docker Swarm cluster for high availability and ease of management/disaster recovery 

## Hosted Services

- Adguard Home
- Jellyfin
- Netbox
- Pangolin

## Hardware

- 2 x Raspberry Pi 4B+ - Using PoE Hats for power and basic cooling
- 2 x Lenovo Micro PCs

## VPS

- 1 x Digital Ocean cloud based Droplet providing the extenal hosting for remote access tools

## [Docker Compose](/docker-compose/)

Files used for the delopyment of services within the docker swarm cluster
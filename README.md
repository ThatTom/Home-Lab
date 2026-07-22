# Hogwarts Homelab

Self hosted debian based home lab running a Docker Swarm cluster for high availability and ease of management/disaster recovery 

## [Hosted Services](/hosted-services/)

Hosted services within the Hogwarts Network/Homelab including those on cloud hosted solutions, changelog version tracking and required documentation hosting

## [Hardware](/hardware/)

- 2 x Raspberry Pi 4B+ - Using PoE Hats for power and basic cooling
- 2 x Lenovo Micro PCs

## [Cloud](/cloud/)

- 1 x Digital Ocean cloud based Droplet providing the external hosting for remote access tools

## [Network](/network/)

- /24 - Local trusted devices
- /26 - Local non-trusted devices/guests
- /26 - IoT Devices

## [Docker Compose](/docker-compose/)

Files used for the deployment of services within the docker swarm cluster
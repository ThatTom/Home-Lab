# Network

## Overview

The network is split into VLANs on `10.10.0.0/16`. The VLAN ID matches the third octet, so `10.10.20.x` is always VLAN 20.

- Router - leaky-cauldron (MikroTik hEX S), bridge `HGLan`
- Switches - floo and portkey (8-port access switches, port 8 is the tagged uplink to the router)
- WAN - PPPoE

Within each /24:

|Range|Use|
|:--:|:--:|
|.1|Router (gateway, DHCP, DNS)|
|.2 - .99|Static / reserved addresses|
|.100 - .199|DHCP pool|

## VLANs

|VLAN|Name|Subnet|Gateway|Purpose|
|:--:|:--:|:--:|:--:|:--:|
|1|Default|192.168.100.0/24|192.168.100.1|Legacy flat network, retired once migration is complete|
|10|Management|10.10.10.0/24|10.10.10.1|Router and switch management|
|20|Servers|10.10.20.0/24|10.10.20.1|Swarm nodes, NAS, Home Assistant|
|30|Trusted|10.10.30.0/24|10.10.30.1|Personal laptops, phones, desktops|
|40|IoT|10.10.40.0/24|10.10.40.1|Smart devices, printer|
|50|Media|10.10.50.0/24|10.10.50.1|TVs, streaming devices, speakers|
|60|Guest|10.10.60.0/24|10.10.60.1|Visitors, internet only|
|70|Ceph|10.10.70.0/24|None|Ceph cluster traffic, not routed|
|80|Work|10.10.80.0/24|10.10.80.1|Work laptop and phone, internet only|
|99|WireGuard|10.10.99.0/24|10.10.99.1|Remote access VPN clients|

> If the work VPN overlaps `10.10.0.0/16`, move Work to `192.168.80.0/24`.

### Firewall Rules

- **Trusted** can reach everything.
- **Management** accepts connections from Trusted and WireGuard only.
- **Servers** can be reached from Trusted, WireGuard, Media (Jellyfin / Traefik 443) and IoT (Home Assistant only).
- **IoT, Media, Guest and Work** get internet and router DNS only.
- **WireGuard** can reach Management, Servers and Trusted.
- **Ceph** is never routed.

## Static Assignments

|Device Name|Role|VLAN|IP Address|
|:--:|:--:|:--:|:--:|
|leaky-cauldron|Router|All|10.10.x.1|
|floo|Access switch|10 Management|10.10.10.2|
|portkey|Access switch|10 Management|10.10.10.3|
|dumbledore|Swarm manager|20 Servers|10.10.20.10|
|flitwick|Swarm manager|20 Servers|10.10.20.11|
|dobby|Swarm worker|20 Servers|10.10.20.20|
|winky|Swarm worker|20 Servers|10.10.20.21|
|gringotts|NAS|20 Servers|10.10.20.30|
|burrow|Home Assistant|20 Servers|10.10.20.40|
|burrow|Home Assistant (IoT leg)|40 IoT|10.10.40.40|
|fawkes|Laptop|30 Trusted|10.10.30.10|
|ollivander|3D printer|40 IoT|10.10.40.10|
|sonorus|Office speaker|50 Media|10.10.50.10|
|howler|Office speaker|50 Media|10.10.50.11|
|dobby|Ceph interface|70 Ceph|10.10.70.20|
|winky|Ceph interface|70 Ceph|10.10.70.21|
|tom-phone|WireGuard peer|99 WireGuard|10.10.99.2|
|tom-laptop|WireGuard peer|99 WireGuard|10.10.99.3|

Management IP for leaky-cauldron is `10.10.10.1`.

### Servers VLAN Ranges

|Range|Use|
|:--:|:--:|
|.10 - .19|Swarm managers|
|.20 - .29|Swarm workers|
|.30 - .39|Storage|
|.40 - .49|Home automation|
|.100 - .199|DHCP|

## WireGuard

- Interface subnet - 10.10.99.0/24
- Port - 51820/udp
- MTU - 1412 (PPPoE)
- Client `AllowedIPs` - `10.10.0.0/16` (split tunnel)
- Client DNS - 10.10.99.1

## Docker Swarm Networks

|Network|Subnet|Use|
|:--:|:--:|:--:|
|proxy|10.200.1.0/24|Services routed through Traefik|
|media|10.200.2.0/24|Jellyfin, Sonarr, Radarr, Seerr|
|backend|10.200.3.0/24|Internal-only databases|
|komodo|10.200.4.0/24|Komodo Core to Periphery|
|ingress|10.0.0.0/24|Swarm default|
|local bridges|10.201.0.0/16|`default-address-pools` in daemon.json|
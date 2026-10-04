[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)
[![GitHub release](https://img.shields.io/github/release/fmainz/ha-ipfire?include_prereleases=&sort=semver&color=blue)](https://github.com/fmainz/ha-ipfire/releases/)
![last commit](https://img.shields.io/github/last-commit/fmainz/ha-ipfire)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
![GitHub total downloads](https://img.shields.io/github/downloads/fmainz/HA-IPFire/total?style=flat-square&color=red)
[![stars](https://img.shields.io/github/stars/fmainz/HA-IPFire)](https://github.com/FMainz/HA-IPFire/stargazers)

# HA-IPFire

## 🇬🇧 English

Home Assistant integration for monitoring IPFire system information, network status, traffic statistics, and internet connection control.

This documentation is also available in 🇩🇪 [German](README-de.md).

## Contents

- [What’s New in This Version](#whats-new-in-this-version)
- [Features](#features)
- [IPFire](#ipfire)
- [IPFire API](#ipfire-api)
  - [IPFire CGI installation](#ipfire-cgi-installation)
- [Sensors](#sensors)
- [Internet connection control](#internet-connection-control)
- [Polling interval](#polling-interval)
- [SSL certificates](#ssl-certificates)
- [Authentication](#authentication)
- [Installation](#installation)
  - [HACS](#hacs)
  - [Manual installation](#manual-installation)
- [Configuration](#configuration)
- [IPFire data](#ipfire-data)
- [Device](#device)
- [Connection control](#connection-control)
- [Home Assistant](#home-assistant)
- [Support](#support)
- [Repository](#repository)
- [License](#license)

---

## What’s New in This Version

### v0.3.3

* Added system information sensors for IPFire version, Pakfire version, kernel version, architecture, CPU model, CPU count, model and vendor.
* Added CPU usage, CPU total and CPU idle sensors.
* Added memory sensors for total, available, free, buffers and cached memory.
* Added disk space sensors for total, used, available space and disk usage.
* Added disk temperature and SMART error sensors.
* Added IPFire uptime sensor.
* Added package update information.
* Added improved icon handling for sensors and network interfaces.
* Network interface icons now dynamically indicate whether an interface is connected or disconnected.

## Features

HA-IPFire provides the following features:

* Download traffic counter
* Upload traffic counter
* Current download speed
* Current upload speed
* Internet connection state
* Internet connection duration
* Connect and Disconnect controls
* Configurable polling interval
* Polling interval from 5 to 60 seconds
* Optional SSL certificate verification
* Username/password authentication
* HACS compatible
* German and English translations

## IPFire

The integration retrieves traffic information from the IPFire endpoint:

```text
/cgi-bin/speed.cgi
```

The default URL is:

```text
https://ipfire.local:444
```

The hostname or IP address can be changed during configuration.

HA-IPFire uses the cumulative traffic counters provided by IPFire to calculate the current transfer rates.

## IPFire API

The optional `api.cgi` script provides additional information and control functions that are not available through `speed.cgi`.

### Connection control

The `api.cgi` script allows HA-IPFire to control the IPFire internet connection directly from Home Assistant.

The following actions are available:

* **Connect** – establishes the internet connection.
* **Disconnect** – disconnects the internet connection.

If **Connect** is pressed while a connection is already active, the current connection is disconnected and re-established.

The connection control uses the native IPFire connection handling provided by the `api.cgi` script.

### System parameters

The `system` section provides the following information:

| Parameter | Description |
| --- | --- |
| `version` | IPFire version |
| `pakfire_version` | Pakfire version |
| `kernel_version` | Linux kernel version |
| `architecture` | System architecture |
| `cpu_model` | CPU model |
| `cpu_count` | Number of CPU cores |
| `model` | System model |
| `vendor` | System vendor |
| `virtual` | Indicates whether the system is virtualized |
| `core_update` | Indicates whether a core update is available |
| `package_updates` | Number of available package updates |
| `uptime` | System uptime in seconds |

#### CPU

| Parameter | Description |
| --- | --- |
| `total` | Total accumulated CPU time |
| `idle` | Accumulated CPU idle time |

#### Memory

| Parameter | Description |
| --- | --- |
| `total` | Total physical memory in bytes |
| `available` | Available memory in bytes |
| `free` | Free memory in bytes |
| `buffers` | Memory used for buffers in bytes |
| `cached` | Memory used for cache in bytes |

#### Disk

Disk space information for the root filesystem is provided under `disk.root`.

| Parameter | Description |
| --- | --- |
| `total` | Total disk space in bytes |
| `used` | Used disk space in bytes |
| `available` | Available disk space in bytes |
| `use_percent` | Disk usage in percent |

Disk I/O statistics for the `sda` device are provided under `disk.sda`.

| Parameter | Description |
| --- | --- |
| `reads` | Number of completed read operations |
| `sectors_read` | Number of sectors read |
| `writes` | Number of completed write operations |
| `sectors_written` | Number of sectors written |
| `io_in_progress` | Number of I/O operations currently in progress |
| `io_time` | Time spent performing I/O operations |

#### SMART

SMART information is provided for the system disk.

| Parameter | Description |
| --- | --- |
| `power_on_hours` | Disk power-on hours |
| `remaining_lifetime` | Remaining disk lifetime in percent |
| `health` | SMART health status |
| `errors` | SMART error count |
| `uncorrectable_errors` | Number of uncorrectable errors |
| `power_cycles` | Number of power cycles |
| `temperature` | Disk temperature |

### Network

The `network` section provides the current state of the IPFire network interfaces.

| Parameter | Description |
| --- | --- |
| `blue` | State of the BLUE network interface |
| `green` | State of the GREEN network interface |
| `orange` | State of the ORANGE network interface |
| `red` | State of the RED network interface |

The values are boolean:

* `true` – the interface is active
* `false` – the interface is inactive

### Services

The `services` section provides the current status of the services managed by IPFire.

| Parameter | Description |
| --- | --- |
| `dhcp` | DHCP server status |
| `web_server` | IPFire web server status |
| `cron` | Cron service status |
| `dns_resolver` | DNS resolver status |
| `logging` | Logging service status |
| `ntp` | NTP service status |
| `ssh` | SSH service status |
| `vpn` | VPN service status |
| `web_proxy` | Web proxy status |
| `ips` | Intrusion Prevention System (IPS) status |
| `ovpn_roadwarrior` | OpenVPN Roadwarrior status |
| `lldp` | LLDP service status |
| `dbus` | D-Bus service status |

The values are boolean:

* `true` – the service is running
* `false` – the service is not running

### Add-ons

The `addons` section provides the current status of supported IPFire add-ons.

The following example shows how an add-on status is represented:

| Parameter | Description |
| --- | --- |
| `transmission.running` | Indicates whether the Transmission add-on is running |

The value is boolean:

* `true` – the add-on is running
* `false` – the add-on is not running

Transmission is used here as an example. The `addons` section can provide status information for other supported add-ons as well.

### Updates

The `system` section provides information about available IPFire updates.

| Parameter | Description |
| --- | --- |
| `core_update` | Indicates whether an IPFire core update is available |
| `package_updates` | Number of available package updates |

The `core_update` value is boolean:

* `true` – a core update is available
* `false` – no core update is available

`package_updates` contains the number of available package updates.

### IPFire CGI installation

The CGI script is included in this repository at:

```text
ipfire/api.cgi
```

The CGI must be installed manually on the IPFire firewall. HACS installs only the Home Assistant integration and cannot copy files to the separate IPFire system.

Copy the CGI to:

```text
/srv/web/ipfire/cgi-bin/api.cgi
```

Then set the correct ownership and permissions:

```bash
chown root:root /srv/web/ipfire/cgi-bin/api.cgi
chmod 755 /srv/web/ipfire/cgi-bin/api.cgi
```

The CGI uses the existing IPFire web interface authentication. No additional CGI credentials are required.

**Security:** The CGI should only be accessible through the trusted IPFire web interface and must not be exposed to untrusted networks.

## Sensors

The integration provides the following sensors:

### Traffic

* **Download** – cumulative download traffic in bytes.
* **Upload** – cumulative upload traffic in bytes.
* **Download Speed** – current download speed.
* **Upload Speed** – current upload speed.

The following sensors and functions require `api.cgi` to be [installed](#ipfire-cgi-installation) on the IPFire firewall.

### Internet connection

* **Connection Duration** – duration of the current internet connection.
* **Connection State** – current IPFire connection state.
* **Connected Since** – time when the current connection was established.
* **External IP** – current external IP address.
* **External Hostname** – current external hostname.

### System

* **IPFire Version**
* **Pakfire Version**
* **Kernel Version**
* **Architecture**
* **CPU Model**
* **CPU Count**
* **Model**
* **Vendor**
* **Uptime**
* **Package Updates**

### CPU

* **CPU Usage**
* **CPU Total**
* **CPU Idle**

### Memory

* **Memory Total**
* **Memory Available**
* **Memory Free**
* **Memory Buffers**
* **Memory Cached**

### Disk

* **Disk Total**
* **Disk Used**
* **Disk Available**
* **Disk Usage**

### SMART

* **Disk Temperature**
* **SMART Errors**

## Internet connection control

HA-IPFire provides two buttons to control the IPFire internet connection:

* **Connect** starts the IPFire internet connection.
* **Disconnect** stops the IPFire internet connection.

The buttons use the dedicated `api.cgi` endpoint on the IPFire firewall. The CGI uses IPFire's native connection control and authentication.

> [!NOTE]
> The function requires `api.cgi` to be [installed](#ipfire-cgi-installation) on the IPFire firewall.

## Polling interval

The polling interval can be configured between:

* **Minimum:** 5 seconds
* **Default:** 30 seconds
* **Maximum:** 60 seconds

The interval can be adjusted in steps of 5 seconds using the slider in the configuration.

A shorter interval provides more frequent updates but also results in more requests to the IPFire firewall.

## SSL certificates

SSL certificate verification can be enabled or disabled during configuration.

Because IPFire installations commonly use self-signed certificates, certificate verification is disabled by default.

If your IPFire installation uses a certificate signed by a trusted certificate authority, SSL verification can be enabled.

## Authentication

The IPFire `speed.cgi` endpoint requires authentication.

HA-IPFire therefore supports:

* Username
* Password

The credentials are configured when adding the integration to Home Assistant.

## Installation

Directly via this button:

[![Open HA-IPFire in HACS](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=FMainz&repository=HA-IPFire&category=integration)

### HACS

HA-IPFire can be installed directly through HACS.

1. Open **HACS**.
2. Select **Integrations**.
3. Search for `HA-IPFire`.
4. Install the integration.
5. Restart Home Assistant.

If HA-IPFire is not available in the standard HACS search, the repository can alternatively be added as a custom repository:

```text
https://github.com/FMainz/HA-IPFire
```

Select **Integration** as the repository type.

After installation, add the integration through:

**Settings → Devices & services → Add integration**

Search for:

**HA-IPFire**

### Manual installation

Copy the following directory:

```text
custom_components/ipfire
```

into:

```text
config/custom_components/ipfire
```

Restart Home Assistant and add IPFire through:

**Settings → Devices & services → Add integration**

## Configuration

During setup, HA-IPFire asks for the following information:

* **IPFire URL** – the hostname or IP address of the IPFire firewall.
* **Username** – the IPFire web interface username.
* **Password** – the corresponding IPFire password.
* **SSL certificate verification** – enables or disables SSL certificate verification.
* **Polling interval** – determines how often HA-IPFire requests updated data from IPFire.

The default IPFire URL is:

```text
https://ipfire.local:444
```

HA-IPFire automatically uses the following endpoints:

```text
/cgi-bin/speed.cgi
```

for traffic data and

```text
/cgi-bin/api.cgi
```

for additional system information, network and service status, update information, and internet connection control.
The polling interval can be configured between **5 and 60 seconds**.

## IPFire data

The data is read directly from IPFire. Traffic statistics are provided by
`speed.cgi`. Additional system, network, service, and update information is
provided through the optional `api.cgi`.

## Device

HA-IPFire creates a single device for the IPFire firewall in Home Assistant.

All sensors and controls provided by the integration are grouped under this device.

## Connection control

HA-IPFire can control the Internet connection of the IPFire firewall directly from Home Assistant.

The following actions are available through the provided buttons:

* **Connect** – establishes the Internet connection.
* **Disconnect** – disconnects the Internet connection.

If Connect is pressed while a connection is already active, the current connection is disconnected and re-established.

## Home Assistant

HA-IPFire uses Home Assistant's native sensor classes, units, and statistics support.

Traffic counters are provided as cumulative, increasing values, allowing Home Assistant to use them for statistics and history.

Current transfer rates are calculated from the traffic counters and are provided as data rates.

## Support

If you encounter a problem or have a suggestion, please open an issue in the GitHub repository:

https://github.com/FMainz/HA-IPFire/issues

## Repository

https://github.com/FMainz/HA-IPFire

## License

HA-IPFire is released under the MIT License.

---

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)
[![GitHub release](https://img.shields.io/github/release/fmainz/ha-ipfire?include_prereleases=&sort=semver&color=blue)](https://github.com/fmainz/ha-ipfire/releases/)
![last commit](https://img.shields.io/github/last-commit/fmainz/ha-ipfire)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
![Package downloads](https://img.shields.io/github/downloads/fmainz/HA-IPFire/total?style=flat-square&color=red&label=Package%20downloads)
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

### v0.3.5

* Development of the IPFire CGI `api.cgi` continues in the standalone [IPFire-API](https://github.com/FMainz/IPFire-API) repository.

### v0.3.4

* Fixed and enabled the download counter.

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

The optional `api.cgi` script extends `speed.cgi` with system information and connection control. It is developed separately in the [IPFire-API project](https://github.com/FMainz/IPFire-API).

### Additional information

In addition to connection status and controls, the API provides information such as:

* IPFire, Pakfire, and kernel versions, plus system vendor, model, and architecture
* CPU model and number of cores
* Memory and disk usage, including I/O statistics and SMART status
* Network interface and IPFire service states
* Installed add-ons and their status
* Available core and package updates

For a complete description of the JSON fields, see the [IPFire-API documentation](https://github.com/FMainz/IPFire-API/blob/main/README.md#endpoint).

### Connection control

The `api.cgi` script allows HA-IPFire to control the IPFire internet connection directly from Home Assistant.

The following actions are available:

* **Connect** – establishes the internet connection.
* **Disconnect** – disconnects the internet connection.

If **Connect** is pressed while a connection is already active, the current connection is disconnected and re-established.

The connection control uses the native IPFire connection handling provided by the `api.cgi` script.

### IPFire CGI installation

The CGI is maintained in the standalone [IPFire-API project](https://github.com/FMainz/IPFire-API). Follow its [installation instructions](https://github.com/FMainz/IPFire-API/blob/main/README.md#installation) to set it up on your IPFire firewall. HACS installs only the Home Assistant integration and cannot copy files to the separate IPFire system.

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

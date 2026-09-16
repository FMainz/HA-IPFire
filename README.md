# HA-IPFire

🇩🇪 [Deutsche Dokumentation](README-de.md)

[![Open HA-IPFire in HACS](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=FMainz&repository=HA-IPFire&category=integration)

## Contents

- [Features](#features)
- [IPFire](#ipfire)
- [Sensors](#sensors)
- [Internet connection control](#internet-connection-control)
  - [IPFire CGI installation](#ipfire-cgi-installation)
- [Polling interval](#polling-interval)
- [SSL certificates](#ssl-certificates)
- [Authentication](#authentication)
- [Installation](#installation)
  - [HACS](#hacs)
  - [Manual installation](#manual-installation)
- [Configuration](#configuration)
- [IPFire data](#ipfire-data)
- [Device](#device)
- [Home Assistant](#home-assistant)
- [Support](#support)
- [Repository](#repository)
- [License](#license)

---

## 🇬🇧 English

Home Assistant integration for monitoring traffic statistics from an IPFire firewall.

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

## Sensors

The integration provides six sensors:

* **Download**
* **Upload**
* **Download Speed**
* **Upload Speed**
* **Connection Duration**
* **Connection State**

**Connection Duration** reports the duration of the current internet connection in seconds.

**Connection State** reports the current IPFire connection state, such as `connected`, `connecting`, or `disconnected`.

The cumulative traffic counters are provided in bytes.

The current transfer rates are calculated from the difference between two consecutive counter readings and are internally provided in bytes per second.

Home Assistant handles unit conversion and display formatting.

## Internet connection control

HA-IPFire provides two buttons to control the IPFire internet connection:

* **Connect** starts the IPFire internet connection.
* **Disconnect** stops the IPFire internet connection.

The buttons use the dedicated `api.cgi` endpoint on the IPFire firewall. The CGI uses IPFire's native connection control and authentication.

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


## Polling interval

The polling interval can be configured between:

* **Minimum:** 5 seconds
* **Default:** 30 seconds
* **Maximum:** 60 seconds

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

* IPFire URL
* Username
* Password
* SSL certificate verification
* Polling interval

The default IPFire URL is:

```text
https://ipfire.local:444
```

HA-IPFire automatically uses the following endpoint for traffic data:

```text
/cgi-bin/speed.cgi
```

The following endpoint is used for internet connection control:

```text
/cgi-bin/api.cgi
```

The polling interval can be configured between **5 and 60 seconds**.

## IPFire data

IPFire provides cumulative traffic counters through `speed.cgi`.

A typical response contains values similar to:

```xml
<inetinfo>
    <rx_kbs>0 kb/s</rx_kbs>
    <tx_kbs>0 kb/s</tx_kbs>
    <rxb>7307842082</rxb>
    <txb>5579282702</txb>
</inetinfo>
```

HA-IPFire uses the cumulative `rxb` and `txb` counters.

The `rx_kbs` and `tx_kbs` values are not used for calculating the current transfer rate.

Instead, the current download and upload speeds are calculated from the difference between two consecutive counter readings.

This also avoids problems with IPFire installations where `rx_kbs` and `tx_kbs` are reported as `0 kb/s`.

## Device

HA-IPFire creates one IPFire device in Home Assistant.

The following sensors are associated with this device:

* Download
* Upload
* Download Speed
* Upload Speed
* Connection Duration
* Connection State

## Home Assistant

HA-IPFire is designed for current Home Assistant versions and uses Home Assistant's native sensor units and statistics support.

The integration provides cumulative traffic counters as increasing values, allowing Home Assistant to use them for statistics and history.

## Support

If you encounter a problem or have a suggestion, please open an issue in the GitHub repository:

https://github.com/FMainz/HA-IPFire/issues

## Repository

https://github.com/FMainz/HA-IPFire

## License

HA-IPFire is released under the MIT License.

---

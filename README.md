# HA-IPFire

Home Assistant integration for IPFire.

HA-IPFire reads cumulative network traffic counters from an
IPFire firewall using `/cgi-bin/speed.cgi`.

## Features

- Download traffic counter
- Upload traffic counter
- Current download rate
- Current upload rate
- Home Assistant long-term statistics
- Configurable IPFire URL
- Username/password authentication
- Optional SSL certificate verification
- Support for self-signed IPFire certificates
- Local polling
- One IPFire device containing all traffic sensors
- HACS compatible

## Sensors

The integration provides four sensors.

### Download

Cumulative received traffic.

Source:

`rxb`

Unit:

`B`

State class:

`total_increasing`

### Upload

Cumulative transmitted traffic.

Source:

`txb`

Unit:

`B`

State class:

`total_increasing`

### Download Rate

Current calculated download rate.

The rate is calculated from two consecutive `rxb`
measurements.

Unit:

`kB/s`

### Upload Rate

Current calculated upload rate.

The rate is calculated from two consecutive `txb`
measurements.

Unit:

`kB/s`

## IPFire API

HA-IPFire accesses:

`/cgi-bin/speed.cgi`

The default IPFire URL is:

`https://ipfire.local:444`

The actual request is therefore:

`https://ipfire.local:444/cgi-bin/speed.cgi`

The hostname or IP address can be changed during setup.

The expected response is:

```xml
<inetinfo>
    <rx_kbs>0 kb/s</rx_kbs>
    <tx_kbs>0 kb/s</tx_kbs>
    <rxb>7307842082</rxb>
    <txb>5579282702</txb>
</inetinfo>

The rx_kbs and tx_kbs values are intentionally ignored.

On some IPFire installations these values are always reported
as 0 kb/s.

The actual transfer rate is calculated from the cumulative
rxb and txb counters.

Installation
HACS

HA-IPFire can be installed through HACS as a custom repository
until it becomes part of the default HACS repository list.

Open HACS.
Select Integrations.
Open the menu in the upper-right corner.
Select Custom repositories.

Add:

https://github.com/FMainz/HA-IPFire

Select Integration.
Add the repository.
Install HA-IPFire.
Restart Home Assistant.

After restarting Home Assistant:

Settings → Devices & services → Add Integration

Search for:

HA-IPFire

Manual installation

Copy the custom_components/ipfire directory into:

config/custom_components/

Restart Home Assistant and add the integration through:

Settings → Devices & services → Add Integration

Configuration

The default URL is:

https://ipfire.local:444

The integration automatically adds:

/cgi-bin/speed.cgi

The following values are required:

IPFire URL
Username
Password
SSL verification

SSL certificate verification can be enabled or disabled.

It is disabled by default because IPFire installations commonly
use self-signed certificates.

If IPFire uses a certificate signed by a trusted certificate
authority, SSL verification can be enabled.

Polling

The integration polls IPFire every 30 seconds.

The transfer rate is calculated from the difference between
two consecutive measurements.

The first measurement has no previous value, so the rate is
initially 0 kB/s.

Device

All sensors are grouped into one device:

IPFire

Sensors:

Download
Upload
Download Rate
Upload Rate
Development

Repository:

https://github.com/FMainz/HA-IPFire

Issues:

https://github.com/FMainz/HA-IPFire/issues

License

MIT License

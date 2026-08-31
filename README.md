# HA-IPFire

Home Assistant integration for monitoring traffic statistics from an IPFire firewall.

## Features

- Download traffic counter
- Upload traffic counter
- Current download speed
- Current upload speed
- Configurable polling interval
- Polling interval from 5 to 60 seconds
- Optional SSL certificate verification
- Username/password authentication
- HACS compatible
- German and English translations

## IPFire

The integration retrieves traffic information from:

`/cgi-bin/speed.cgi`

Default URL:

`https://ipfire.local:444`

The hostname or IP address can be changed during configuration.

## Sensors

The integration provides four sensors:

- Download
- Upload
- Download Speed
- Upload Speed

The cumulative traffic counters are provided in bytes.

The current transfer rates are calculated from the difference between two counter readings and are internally provided in bytes per second.

Home Assistant handles unit conversion and display formatting.

## Polling interval

The polling interval can be configured between:

- Minimum: 5 seconds
- Default: 30 seconds
- Maximum: 60 seconds

## SSL certificates

SSL certificate verification can be enabled or disabled during configuration.

Because IPFire installations commonly use self-signed certificates, certificate verification is disabled by default.

## Installation

### HACS

Search for `HA-IPFire` in HACS.

Alternatively, add this repository as a custom repository in HACS.

### Manual installation

Copy the `custom_components/ipfire` directory into:

`config/custom_components/ipfire`

Restart Home Assistant and add IPFire through:

Settings → Devices & services → Add integration

## License

MIT

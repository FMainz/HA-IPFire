from __future__ import annotations

import logging
import time
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from datetime import timedelta

import aiohttp

from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    UpdateFailed,
)

from .const import DOMAIN, API_PATH
_LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class IPFireSystemData:
    """Represent system information received from IPFire."""

    version: str | None
    pakfire_version: str | None
    kernel_version: str | None
    architecture: str | None
    cpu_model: str | None
    cpu_count: int | None
    model: str | None
    vendor: str | None
    memory: int | None
    root_size: int | None
    virtual: bool | None
    core_update: bool | None
    package_updates: int | None


@dataclass(frozen=True, slots=True)
class IPFireNetworkData:
    """Represent network information received from IPFire."""

    blue: bool | None
    green: bool | None
    orange: bool | None
    red: bool | None


@dataclass(frozen=True, slots=True)
class IPFireData:
    """Represent data received from IPFire."""

    rxb: int
    txb: int
    rx_rate: float
    tx_rate: float
    connection_state: str
    connected_since: int | None
    connection_duration: int
    connection_duration_text: str
    profile: str
    external_ip: str
    external_hostname: str
    system: IPFireSystemData
    network: IPFireNetworkData
    services: dict[str, bool]
    addons: dict[str, dict[str, bool]]


class IPFireCoordinator(DataUpdateCoordinator[IPFireData]):
    """Coordinate data updates and actions for IPFire."""

    def __init__(
        self,
        hass: HomeAssistant,
        session: aiohttp.ClientSession,
        base_url: str,
        username: str,
        password: str,
        verify_ssl: bool,
        update_interval: timedelta,
    ) -> None:
        """Initialize the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=update_interval,
            always_update=False,
        )

        self.session = session
        self.base_url = base_url.rstrip("/")
        self.username = username
        self.password = password
        self.verify_ssl = verify_ssl

        self._previous_rx_bytes: int | None = None
        self._previous_tx_bytes: int | None = None
        self._previous_timestamp: float | None = None

    @property
    def api_url(self) -> str:
        """Return the IPFire API URL."""
        return f"{self.base_url}{API_PATH}"

    @property
    def speed_url(self) -> str:
        """Return the IPFire speed.cgi URL."""
        return f"{self.base_url}/cgi-bin/speed.cgi"

    def _auth(self) -> aiohttp.BasicAuth:
        """Return HTTP basic authentication."""
        return aiohttp.BasicAuth(self.username, self.password)

    async def _async_update_data(self) -> IPFireData:
        """Fetch and calculate data from IPFire."""
        try:
            async with self.session.get(
                self.api_url,
                auth=self._auth(),
                ssl=self.verify_ssl,
                timeout=aiohttp.ClientTimeout(total=10),
            ) as response:
                if response.status in (401, 403):
                    raise ConfigEntryAuthFailed(
                        "Invalid IPFire username or password"
                    )

                if response.status == 404:
                    _LOGGER.debug(
                        "HA-IPFire CGI not available, falling back to speed.cgi"
                    )

                    async with self.session.get(
                        self.speed_url,
                        auth=self._auth(),
                        ssl=self.verify_ssl,
                        timeout=aiohttp.ClientTimeout(total=10),
                    ) as speed_response:
                        if speed_response.status in (401, 403):
                            raise ConfigEntryAuthFailed(
                                "Invalid IPFire username or password"
                            )

                        speed_response.raise_for_status()
                        payload = await speed_response.text()
                        payload = self._parse_speed_cgi(payload)

                else:
                    response.raise_for_status()
                    payload = await response.json(content_type=None)

        except ConfigEntryAuthFailed:
            raise

        except (aiohttp.ClientError, ValueError) as err:
            raise UpdateFailed(
                f"Unable to read data from IPFire: {err}"
            ) from err

        try:
            connection = payload["connection"]
            traffic = payload["traffic"]
            system = payload.get("system", {})
            network = payload.get("network", {})
            services = payload.get("services", {})
            addons = payload.get("addons", {})
            if not isinstance(connection, dict):
                raise ValueError("Invalid connection data from IPFire")

            if not isinstance(traffic, dict):
                raise ValueError("Invalid traffic data from IPFire")

            if not isinstance(system, dict):
                raise ValueError("Invalid system data from IPFire")

            if not isinstance(network, dict):
                raise ValueError("Invalid network data from IPFire")

            if not isinstance(services, dict):
                raise ValueError("Invalid services data from IPFire")

            if not isinstance(addons, dict):
                raise ValueError("Invalid addons data from IPFire")
            connection_state = str(connection.get("state", "unavailable"))

            if "rx_bytes" not in traffic:
                raise ValueError("Missing RX traffic data from IPFire")

            if "tx_bytes" not in traffic:
                raise ValueError("Missing TX traffic data from IPFire")
            rx_value = traffic.get("rx_bytes")
            tx_value = traffic.get("tx_bytes")

            if rx_value is None:
                rx_bytes = self._previous_rx_bytes or 0
            else:
                rx_bytes = self._parse_counter(rx_value)

            if tx_value is None:
                tx_bytes = self._previous_tx_bytes or 0
            else:
                tx_bytes = self._parse_counter(tx_value)

            connected_since = self._parse_optional_int(
                connection.get("connected_since")
            )
            connection_duration = int(connection.get("duration", 0))
            connection_duration_text = str(
                connection.get("duration_text", "")
            )
            profile = str(connection.get("profile", ""))
            external_ip = str(connection.get("external_ip", ""))
            external_hostname = str(connection.get("external_hostname", ""))

            system_data = IPFireSystemData(
                version=system.get("version"),
                pakfire_version=system.get("pakfire_version"),
                kernel_version=system.get("kernel_version"),
                architecture=system.get("architecture"),
                cpu_model=system.get("cpu_model"),
                cpu_count=system.get("cpu_count"),
                model=system.get("model"),
                vendor=system.get("vendor"),
                memory=system.get("memory"),
                root_size=system.get("root_size"),
                virtual=system.get("virtual"),
                core_update=system.get("core_update"),
                package_updates=system.get("package_updates"),
            )

            network_data = IPFireNetworkData(
                blue=network.get("blue"),
                green=network.get("green"),
                orange=network.get("orange"),
                red=network.get("red"),
            )

        except (KeyError, TypeError, ValueError) as err:
            raise UpdateFailed(
                "Invalid JSON response from IPFire"
            ) from err

        now = time.monotonic()
        rx_rate = 0.0
        tx_rate = 0.0

        if (
            connection_state != "closed"
            and self._previous_rx_bytes is not None
            and self._previous_tx_bytes is not None
            and self._previous_timestamp is not None
        ):
            elapsed = now - self._previous_timestamp

            if elapsed > 0:
                rx_difference = rx_bytes - self._previous_rx_bytes
                tx_difference = tx_bytes - self._previous_tx_bytes

                if rx_difference >= 0:
                    rx_rate = rx_difference / elapsed

                if tx_difference >= 0:
                    tx_rate = tx_difference / elapsed

        self._previous_rx_bytes = rx_bytes
        self._previous_tx_bytes = tx_bytes
        self._previous_timestamp = now

        return IPFireData(
            rxb=rx_bytes,
            txb=tx_bytes,
            rx_rate=rx_rate,
            tx_rate=tx_rate,
            connection_state=connection_state,
            connected_since=connected_since,
            connection_duration=connection_duration,
            connection_duration_text=connection_duration_text,
            profile=profile,
            external_ip=external_ip,
            external_hostname=external_hostname,
            system=system_data,
            network=network_data,
            services=services,
            addons=addons,
        )

    async def async_connect(self) -> None:
        """Connect the IPFire Internet connection."""
        await self._async_connection_action("connect")

    async def async_disconnect(self) -> None:
        """Disconnect the IPFire Internet connection."""
        await self._async_connection_action("disconnect")

    async def _async_connection_action(self, action: str) -> None:
        """Execute a connection action on IPFire."""
        if action not in {"connect", "disconnect"}:
            raise ValueError(f"Unsupported IPFire action: {action}")

        try:
            async with self.session.post(
                self.api_url,
                auth=self._auth(),
                ssl=self.verify_ssl,
                headers={"X-HA-IPFire-API": "1"},
                data={"action": action},
                timeout=aiohttp.ClientTimeout(total=15),
            ) as response:
                if response.status in (401, 403):
                    raise ConfigEntryAuthFailed(
                        "Invalid IPFire username or password"
                    )

                if response.status >= 400:
                    try:
                        payload = await response.json(content_type=None)
                    except (ValueError, TypeError):
                        payload = {}

                    error = payload.get("error", "unknown_error")
                    raise UpdateFailed(
                        f"IPFire action '{action}' failed: {error}"
                    )

                payload = await response.json(content_type=None)

                if payload.get("result") != "ok":
                    raise UpdateFailed(
                        f"IPFire action '{action}' failed: "
                        f"{payload.get('result', 'unknown_error')}"
                    )

        except ConfigEntryAuthFailed:
            raise

        except (aiohttp.ClientError, ValueError) as err:
            raise UpdateFailed(
                f"Unable to execute IPFire action '{action}': {err}"
            ) from err

        # Refresh immediately so HA sees the new connection state.
        await self.async_request_refresh()

    @staticmethod
    def _parse_speed_cgi(payload: str) -> dict:
        """Parse the XML response from IPFire speed.cgi."""

        root = ET.fromstring(payload)

        return {
            "connection": {
                "state": "unavailable",
                "connected_since": None,
                "duration": 0,
                "duration_text": "",
                "profile": "",
            },
            "traffic": {
                "rx_bytes": root.findtext("rxb", "0"),
                "tx_bytes": root.findtext("txb", "0"),
            },
            "system": {},
            "network": {},
            "services": {},
            "addons": {},
        }

    @staticmethod
    def _parse_counter(value: object) -> int:
        """Parse a byte counter returned by IPFire."""
        if value is None:
            raise ValueError("Missing counter value")

        return int(str(value))

    @staticmethod
    def _parse_optional_int(value: object) -> int | None:
        """Parse an optional integer returned by IPFire."""
        if value is None:
            return None

        return int(str(value))

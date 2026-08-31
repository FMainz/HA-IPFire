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

from .const import DOMAIN, SPEED_PATH


_LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class IPFireData:
    """Represent data received from IPFire."""

    rxb: int
    txb: int
    rx_rate: float
    tx_rate: float


class IPFireCoordinator(DataUpdateCoordinator[IPFireData]):
    """Coordinate data updates from IPFire."""

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

    async def _async_update_data(self) -> IPFireData:
        """Fetch and calculate traffic data from IPFire."""

        url = f"{self.base_url}{SPEED_PATH}"

        try:
            async with self.session.get(
                url,
                auth=aiohttp.BasicAuth(
                    self.username,
                    self.password,
                ),
                ssl=self.verify_ssl,
                timeout=aiohttp.ClientTimeout(total=10),
            ) as response:
                if response.status in (401, 403):
                    raise ConfigEntryAuthFailed(
                        "Invalid IPFire username or password"
                    )

                response.raise_for_status()
                content = await response.text()

        except ConfigEntryAuthFailed:
            raise

        except aiohttp.ClientError as err:
            raise UpdateFailed(
                f"Unable to connect to IPFire: {err}"
            ) from err

        except TimeoutError as err:
            raise UpdateFailed(
                "Timeout while connecting to IPFire"
            ) from err

        try:
            root = ET.fromstring(content)

            rx_bytes = self._parse_counter(
                root.findtext("rxb")
            )
            tx_bytes = self._parse_counter(
                root.findtext("txb")
            )

        except (ET.ParseError, ValueError) as err:
            raise UpdateFailed(
                "Invalid XML response from IPFire"
            ) from err

        now = time.monotonic()

        rx_rate = 0.0
        tx_rate = 0.0

        if (
            self._previous_rx_bytes is not None
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
        )

    @staticmethod
    def _parse_counter(value: str | None) -> int:
        """Parse a byte counter returned by IPFire."""

        if value is None:
            raise ValueError("Missing counter value")

        return int(value.strip().split()[0])

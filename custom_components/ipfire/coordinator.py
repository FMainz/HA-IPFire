from __future__ import annotations

from datetime import datetime, timedelta
import logging
import xml.etree.ElementTree as ET

import aiohttp

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    UpdateFailed,
)
from homeassistant.util import dt as dt_util

from .const import SPEED_PATH


_LOGGER = logging.getLogger(__name__)


class IPFireCoordinator(
    DataUpdateCoordinator[dict[str, float | int]]
):
    """Fetch traffic counters from IPFire."""

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

        self.session = session
        self.base_url = base_url.rstrip("/")
        self.username = username
        self.password = password
        self.verify_ssl = verify_ssl

        self._previous_rxb: int | None = None
        self._previous_txb: int | None = None
        self._previous_time: datetime | None = None

        super().__init__(
            hass,
            _LOGGER,
            name="IPFire",
            update_interval=update_interval,
        )

    @property
    def speed_url(self) -> str:
        """Return the speed.cgi URL."""
        return f"{self.base_url}{SPEED_PATH}"

    async def _async_update_data(
        self,
    ) -> dict[str, float | int]:
        """Fetch and parse speed.cgi."""

        try:
            async with self.session.get(
                self.speed_url,
                auth=aiohttp.BasicAuth(
                    self.username,
                    self.password,
                ),
                ssl=(
                    self.verify_ssl
                    if self.verify_ssl
                    else False
                ),
                timeout=aiohttp.ClientTimeout(
                    total=10
                ),
            ) as response:

                response.raise_for_status()
                content = await response.text()

        except aiohttp.ClientResponseError as err:
            raise UpdateFailed(
                f"IPFire HTTP error "
                f"{err.status}: {err.message}"
            ) from err

        except (
            aiohttp.ClientError,
            TimeoutError,
        ) as err:
            raise UpdateFailed(
                f"Unable to connect to IPFire: {err}"
            ) from err

        try:
            root = ET.fromstring(content)

            rxb_text = root.findtext("rxb")
            txb_text = root.findtext("txb")

            if rxb_text is None:
                raise ValueError(
                    "XML does not contain rxb"
                )

            if txb_text is None:
                raise ValueError(
                    "XML does not contain txb"
                )

            rxb = int(rxb_text.strip())
            txb = int(txb_text.strip())

            if rxb < 0 or txb < 0:
                raise ValueError(
                    "Traffic counters must not be negative"
                )

        except (
            ET.ParseError,
            ValueError,
        ) as err:
            raise UpdateFailed(
                f"Invalid IPFire XML response: {err}"
            ) from err

        # Calculate current transfer rates.
        now = dt_util.utcnow()

        rx_rate = 0.0
        tx_rate = 0.0

        if (
            self._previous_time is not None
            and self._previous_rxb is not None
            and self._previous_txb is not None
        ):
            elapsed = (
                now - self._previous_time
            ).total_seconds()

            if elapsed > 0:
                rx_delta = rxb - self._previous_rxb
                tx_delta = txb - self._previous_txb

                # A decrease means that IPFire's counters
                # were reset. In that case don't report
                # a negative transfer rate.
                if rx_delta >= 0:
                    rx_rate = rx_delta / elapsed

                if tx_delta >= 0:
                    tx_rate = tx_delta / elapsed

        self._previous_rxb = rxb
        self._previous_txb = txb
        self._previous_time = now

        return {
            "rxb": rxb,
            "txb": txb,
            "rx_rate": rx_rate,
            "tx_rate": tx_rate,
        }
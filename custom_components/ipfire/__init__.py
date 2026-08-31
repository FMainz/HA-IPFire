from __future__ import annotations

from datetime import timedelta

import aiohttp

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import (
    CONF_PASSWORD,
    CONF_URL,
    CONF_USERNAME,
    CONF_VERIFY_SSL,
    DATA_COORDINATOR,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
)
from .coordinator import IPFireCoordinator


PLATFORMS: list[str] = ["sensor"]


async def async_setup(
    hass: HomeAssistant,
    config: dict,
) -> bool:
    """Set up the IPFire integration."""
    hass.data.setdefault(DOMAIN, {})
    return True


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
) -> bool:
    """Set up IPFire from a config entry."""

    session = aiohttp.ClientSession()

    coordinator = IPFireCoordinator(
        hass=hass,
        session=session,
        base_url=entry.data[CONF_URL],
        username=entry.data[CONF_USERNAME],
        password=entry.data[CONF_PASSWORD],
        verify_ssl=entry.data[CONF_VERIFY_SSL],
        update_interval=timedelta(
            seconds=DEFAULT_SCAN_INTERVAL
        ),
    )

    await coordinator.async_config_entry_first_refresh()

    hass.data[DOMAIN][entry.entry_id] = {
        DATA_COORDINATOR: coordinator,
        "session": session,
    }

    await hass.config_entries.async_forward_entry_setups(
        entry,
        PLATFORMS,
    )

    return True


async def async_unload_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
) -> bool:
    """Unload an IPFire config entry."""

    unload_ok = await hass.config_entries.async_unload_platforms(
        entry,
        PLATFORMS,
    )

    data = hass.data[DOMAIN].pop(entry.entry_id)

    await data["session"].close()

    return unload_ok
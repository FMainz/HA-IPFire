from __future__ import annotations

from dataclasses import dataclass
from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import (
    CONF_PASSWORD,
    CONF_SCAN_INTERVAL,
    CONF_URL,
    CONF_USERNAME,
    CONF_VERIFY_SSL,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
)
from .coordinator import IPFireCoordinator


PLATFORMS: list[str] = ["button", "sensor"]

CONFIG_SCHEMA = cv.config_entry_only_config_schema(DOMAIN)

CONFIG_ENTRY_VERSION = 2


@dataclass(slots=True)
class IPFireRuntimeData:
    """Runtime data for HA-IPFire."""

    coordinator: IPFireCoordinator


type IPFireConfigEntry = ConfigEntry[IPFireRuntimeData]


async def async_migrate_entry(
    hass: HomeAssistant,
    config_entry: IPFireConfigEntry,
) -> bool:
    """Migrate an existing HA-IPFire config entry."""

    if config_entry.version == 1:
        hass.config_entries.async_update_entry(
            config_entry,
            version=CONFIG_ENTRY_VERSION,
        )

    return True


async def async_setup_entry(
    hass: HomeAssistant,
    entry: IPFireConfigEntry,
) -> bool:
    """Set up HA-IPFire from a config entry."""

    session = async_get_clientsession(hass)

    scan_interval = entry.options.get(
        CONF_SCAN_INTERVAL,
        DEFAULT_SCAN_INTERVAL,
    )

    coordinator = IPFireCoordinator(
        hass=hass,
        session=session,
        base_url=entry.data[CONF_URL],
        username=entry.data[CONF_USERNAME],
        password=entry.data[CONF_PASSWORD],
        verify_ssl=entry.data[CONF_VERIFY_SSL],
        update_interval=timedelta(
            seconds=scan_interval,
        ),
    )

    await coordinator.async_config_entry_first_refresh()

    entry.runtime_data = IPFireRuntimeData(
        coordinator=coordinator,
    )

    await hass.config_entries.async_forward_entry_setups(
        entry,
        PLATFORMS,
    )

    return True


async def async_unload_entry(
    hass: HomeAssistant,
    entry: IPFireConfigEntry,
) -> bool:
    """Unload HA-IPFire."""

    return await hass.config_entries.async_unload_platforms(
        entry,
        PLATFORMS,
    )
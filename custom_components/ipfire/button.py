from __future__ import annotations

from dataclasses import dataclass

from homeassistant.components.button import ButtonEntity, ButtonEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .coordinator import IPFireCoordinator


PARALLEL_UPDATES = 1


@dataclass(frozen=True, kw_only=True)
class IPFireButtonDescription(ButtonEntityDescription):
    """Describe an IPFire button."""

    action: str


BUTTONS: tuple[IPFireButtonDescription, ...] = (
    IPFireButtonDescription(
        key="connect",
        translation_key="connect",
        icon="mdi:lan-connect",
        action="connect",
    ),
    IPFireButtonDescription(
        key="disconnect",
        translation_key="disconnect",
        icon="mdi:lan-disconnect",
        action="disconnect",
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up IPFire buttons."""

    coordinator: IPFireCoordinator = entry.runtime_data.coordinator

    async_add_entities(
        IPFireConnectionButton(
            coordinator,
            entry,
            description,
        )
        for description in BUTTONS
    )


class IPFireConnectionButton(
    CoordinatorEntity[IPFireCoordinator],
    ButtonEntity,
):
    """Represent an IPFire connection control button."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: IPFireCoordinator,
        entry: ConfigEntry,
        description: IPFireButtonDescription,
    ) -> None:
        """Initialize the button."""

        super().__init__(coordinator)

        self.entity_description = description
        self._attr_unique_id = f"{entry.entry_id}_{description.key}"
        self._attr_device_info = DeviceInfo(
            identifiers={("ipfire", entry.entry_id)},
            name="IPFire",
            manufacturer="IPFire",
            model="Firewall",
        )

    async def async_press(self) -> None:
        """Handle the button press."""

        if self.entity_description.action == "connect":
            await self.coordinator.async_connect()
        else:
            await self.coordinator.async_disconnect()
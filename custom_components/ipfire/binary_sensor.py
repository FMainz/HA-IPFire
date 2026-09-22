from __future__ import annotations

from dataclasses import dataclass

from homeassistant.components.binary_sensor import (
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .coordinator import IPFireCoordinator


PARALLEL_UPDATES = 0


@dataclass(frozen=True, kw_only=True)
class IPFireBinarySensorDescription(BinarySensorEntityDescription):
    """Describe an IPFire binary sensor."""

    value_key: str
    data_group: str = "root"
    entity_registry_enabled_default: bool = True


BINARY_SENSORS: tuple[IPFireBinarySensorDescription, ...] = (
    IPFireBinarySensorDescription(
        key="virtual",
        translation_key="virtual",
        value_key="virtual",
        data_group="system",
        entity_registry_enabled_default=False,
    ),
    IPFireBinarySensorDescription(
        key="core_update",
        translation_key="core_update",
        value_key="core_update",
        data_group="system",
        entity_registry_enabled_default=False,
    ),
    IPFireBinarySensorDescription(
        key="network_blue",
        translation_key="network_blue",
        value_key="blue",
        data_group="network",
    ),
    IPFireBinarySensorDescription(
        key="network_green",
        translation_key="network_green",
        value_key="green",
        data_group="network",
    ),
    IPFireBinarySensorDescription(
        key="network_orange",
        translation_key="network_orange",
        value_key="orange",
        data_group="network",
    ),
    IPFireBinarySensorDescription(
        key="network_red",
        translation_key="network_red",
        value_key="red",
        data_group="network",
    ),
    IPFireBinarySensorDescription(
        key="service_dhcp",
        translation_key="service_dhcp",
        value_key="dhcp",
        data_group="services",
        icon="mdi:ip-network",
        entity_registry_enabled_default=False,
    ),
    IPFireBinarySensorDescription(
        key="service_web_server",
        translation_key="service_web_server",
        value_key="web_server",
        data_group="services",
        icon="mdi:web",
        entity_registry_enabled_default=False,
    ),
    IPFireBinarySensorDescription(
        key="service_cron",
        translation_key="service_cron",
        value_key="cron",
        data_group="services",
        icon="mdi:clock-outline",
        entity_registry_enabled_default=False,
    ),
    IPFireBinarySensorDescription(
        key="service_dns_resolver",
        translation_key="service_dns_resolver",
        value_key="dns_resolver",
        data_group="services",
        icon="mdi:dns",
        entity_registry_enabled_default=False,
    ),
    IPFireBinarySensorDescription(
        key="service_logging",
        translation_key="service_logging",
        value_key="logging",
        data_group="services",
        icon="mdi:text-box-search-outline",
        entity_registry_enabled_default=False,
    ),
    IPFireBinarySensorDescription(
        key="service_ntp",
        translation_key="service_ntp",
        value_key="ntp",
        data_group="services",
        icon="mdi:timer-sync-outline",
        entity_registry_enabled_default=False,
    ),
    IPFireBinarySensorDescription(
        key="service_ssh",
        translation_key="service_ssh",
        value_key="ssh",
        data_group="services",
        icon="mdi:console",
        entity_registry_enabled_default=False,
    ),
    IPFireBinarySensorDescription(
        key="service_vpn",
        translation_key="service_vpn",
        value_key="vpn",
        data_group="services",
        icon="mdi:vpn",
        entity_registry_enabled_default=False,
    ),
    IPFireBinarySensorDescription(
        key="service_web_proxy",
        translation_key="service_web_proxy",
        value_key="web_proxy",
        data_group="services",
        icon="mdi:server-network",
        entity_registry_enabled_default=False,
    ),
    IPFireBinarySensorDescription(
        key="service_ips",
        translation_key="service_ips",
        value_key="ips",
        data_group="services",
        icon="mdi:shield-alert-outline",
        entity_registry_enabled_default=False,
    ),
    IPFireBinarySensorDescription(
        key="service_ovpn_roadwarrior",
        translation_key="service_ovpn_roadwarrior",
        value_key="ovpn_roadwarrior",
        data_group="services",
        icon="mdi:vpn",
        entity_registry_enabled_default=False,
    ),
    IPFireBinarySensorDescription(
        key="service_lldp",
        translation_key="service_lldp",
        value_key="lldp",
        data_group="services",
        icon="mdi:lan-connect",
        entity_registry_enabled_default=False,
    ),
    IPFireBinarySensorDescription(
        key="service_dbus",
        translation_key="service_dbus",
        value_key="dbus",
        data_group="services",
        icon="mdi:bus",
        entity_registry_enabled_default=False,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up IPFire binary sensors."""

    coordinator: IPFireCoordinator = entry.runtime_data.coordinator

    entities = [
        IPFireBinarySensor(
            coordinator,
            entry,
            description,
        )
        for description in BINARY_SENSORS
    ]

    if coordinator.data is not None:
        entities.extend(
            IPFireAddonBinarySensor(
                coordinator,
                entry,
                addon_name,
            )
            for addon_name in coordinator.data.addons
        )

    async_add_entities(entities)


class IPFireAddonBinarySensor(
    CoordinatorEntity[IPFireCoordinator],
    BinarySensorEntity,
):
    """Represent an IPFire add-on binary sensor."""

    _attr_has_entity_name = True
    _attr_entity_registry_enabled_default = False

    def __init__(
        self,
        coordinator: IPFireCoordinator,
        entry: ConfigEntry,
        addon_name: str,
    ) -> None:
        """Initialize the add-on binary sensor."""

        super().__init__(coordinator)

        self._addon_name = addon_name
        self._attr_unique_id = f"{entry.entry_id}_addon_{addon_name}"
        self._attr_name = addon_name.replace("_", " ").title()
        self._attr_icon = "mdi:puzzle"

        self._attr_device_info = DeviceInfo(
            identifiers={("ipfire", entry.entry_id)},
            name="IPFire",
            manufacturer="IPFire",
            model="Firewall",
        )

    @property
    def is_on(self) -> bool | None:
        """Return whether the IPFire add-on is running."""

        if self.coordinator.data is None:
            return None

        addon = self.coordinator.data.addons.get(self._addon_name)

        if not isinstance(addon, dict):
            return None

        return addon.get("running")


class IPFireBinarySensor(
    CoordinatorEntity[IPFireCoordinator],
    BinarySensorEntity,
):
    """Represent an IPFire binary sensor."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: IPFireCoordinator,
        entry: ConfigEntry,
        description: IPFireBinarySensorDescription,
    ) -> None:
        """Initialize the binary sensor."""

        super().__init__(coordinator)

        self.entity_description = description
        self._attr_unique_id = f"{entry.entry_id}_{description.key}"
        self._attr_device_info = DeviceInfo(
            identifiers={("ipfire", entry.entry_id)},
            name="IPFire",
            manufacturer="IPFire",
            model="Firewall",
        )

    @property
    def is_on(self) -> bool | None:
        """Return the current binary sensor state."""

        if self.coordinator.data is None:
            return None

        if self.entity_description.data_group == "system":
            data = self.coordinator.data.system
        elif self.entity_description.data_group == "network":
            data = self.coordinator.data.network
        elif self.entity_description.data_group == "services":
            return self.coordinator.data.services.get(
                self.entity_description.value_key
            )
        else:
            data = self.coordinator.data

        return getattr(
            data,
            self.entity_description.value_key,
            None,
        )

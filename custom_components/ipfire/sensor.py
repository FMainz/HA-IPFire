from __future__ import annotations

from dataclasses import dataclass

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfDataRate, UnitOfInformation, UnitOfTime
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.util import dt as dt_util

from .coordinator import IPFireCoordinator


PARALLEL_UPDATES = 0


@dataclass(frozen=True, kw_only=True)
class IPFireSensorDescription(SensorEntityDescription):
    """Describe an IPFire sensor."""

    value_key: str
    data_group: str = "root"
    entity_registry_enabled_default: bool = True


SENSORS: tuple[IPFireSensorDescription, ...] = (
    IPFireSensorDescription(
        key="rxb",
        translation_key="download",
        value_key="rxb",
        device_class=SensorDeviceClass.DATA_SIZE,
        state_class=SensorStateClass.TOTAL_INCREASING,
        native_unit_of_measurement=UnitOfInformation.BYTES,
        suggested_unit_of_measurement=UnitOfInformation.MEGABYTES,
        suggested_display_precision=1,
    ),
    IPFireSensorDescription(
        key="txb",
        translation_key="upload",
        value_key="txb",
        device_class=SensorDeviceClass.DATA_SIZE,
        state_class=SensorStateClass.TOTAL_INCREASING,
        native_unit_of_measurement=UnitOfInformation.BYTES,
        suggested_unit_of_measurement=UnitOfInformation.MEGABYTES,
        suggested_display_precision=1,
    ),
    IPFireSensorDescription(
        key="rx_rate",
        translation_key="download_rate",
        value_key="rx_rate",
        device_class=SensorDeviceClass.DATA_RATE,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfDataRate.BYTES_PER_SECOND,
        suggested_unit_of_measurement=UnitOfDataRate.KILOBYTES_PER_SECOND,
        suggested_display_precision=1,
    ),
    IPFireSensorDescription(
        key="tx_rate",
        translation_key="upload_rate",
        value_key="tx_rate",
        device_class=SensorDeviceClass.DATA_RATE,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfDataRate.BYTES_PER_SECOND,
        suggested_unit_of_measurement=UnitOfDataRate.KILOBYTES_PER_SECOND,
        suggested_display_precision=1,
    ),
    IPFireSensorDescription(
        key="connection_duration",
        translation_key="connection_duration",
        value_key="connection_duration",
        device_class=SensorDeviceClass.DURATION,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfTime.SECONDS,
        suggested_unit_of_measurement=UnitOfTime.HOURS,
        suggested_display_precision=1,
    ),
    IPFireSensorDescription(
        key="connection_duration_text",
        translation_key="connection_duration_text",
        value_key="connection_duration_text",
        entity_registry_enabled_default=False,
    ),
    IPFireSensorDescription(
        key="connection_state",
        translation_key="connection_state",
        value_key="connection_state",
    ),
    IPFireSensorDescription(
        key="connected_since",
        translation_key="connected_since",
        value_key="connected_since",
        device_class=SensorDeviceClass.TIMESTAMP,
        entity_registry_enabled_default=False,
    ),
    IPFireSensorDescription(
        key="external_ip",
        translation_key="external_ip",
        value_key="external_ip",
        entity_registry_enabled_default=False,
    ),
    IPFireSensorDescription(
        key="external_hostname",
        translation_key="external_hostname",
        value_key="external_hostname",
        entity_registry_enabled_default=False,
    ),
    IPFireSensorDescription(
        key="system_version",
        translation_key="system_version",
        value_key="version",
        data_group="system",
    ),
    IPFireSensorDescription(
        key="pakfire_version",
        translation_key="pakfire_version",
        value_key="pakfire_version",
        data_group="system",
        entity_registry_enabled_default=False,
    ),
    IPFireSensorDescription(
        key="kernel_version",
        translation_key="kernel_version",
        value_key="kernel_version",
        data_group="system",
        entity_registry_enabled_default=False,
    ),
    IPFireSensorDescription(
        key="architecture",
        translation_key="architecture",
        value_key="architecture",
        data_group="system",
        entity_registry_enabled_default=False,
    ),
    IPFireSensorDescription(
        key="cpu_model",
        translation_key="cpu_model",
        value_key="cpu_model",
        data_group="system",
        entity_registry_enabled_default=False,
    ),
    IPFireSensorDescription(
        key="model",
        translation_key="model",
        value_key="model",
        data_group="system",
        entity_registry_enabled_default=False,
    ),
    IPFireSensorDescription(
        key="vendor",
        translation_key="vendor",
        value_key="vendor",
        data_group="system",
        entity_registry_enabled_default=False,
    ),
    IPFireSensorDescription(
        key="cpu_count",
        translation_key="cpu_count",
        value_key="cpu_count",
        data_group="system",
        entity_registry_enabled_default=False,
    ),
    IPFireSensorDescription(
        key="uptime",
        translation_key="uptime",
        value_key="uptime",
        data_group="system",
        device_class=SensorDeviceClass.DURATION,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfTime.SECONDS,
        suggested_unit_of_measurement=UnitOfTime.HOURS,
        suggested_display_precision=1,
        entity_registry_enabled_default=False,
    ),
    IPFireSensorDescription(
        key="cpu_total",
        translation_key="cpu_total",
        value_key="cpu_total",
        data_group="system",
        state_class=SensorStateClass.TOTAL_INCREASING,
        entity_registry_enabled_default=False,
    ),
    IPFireSensorDescription(
        key="cpu_idle",
        translation_key="cpu_idle",
        value_key="cpu_idle",
        data_group="system",
        state_class=SensorStateClass.TOTAL_INCREASING,
        entity_registry_enabled_default=False,
    ),
    IPFireSensorDescription(
        key="cpu_usage",
        translation_key="cpu_usage",
        value_key="cpu_usage",
        data_group="system",
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement="%",
        suggested_display_precision=1,
    ),
    IPFireSensorDescription(
        key="memory_total",
        translation_key="memory_total",
        value_key="memory_total",
        data_group="system",
        device_class=SensorDeviceClass.DATA_SIZE,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfInformation.BYTES,
        suggested_display_precision=1,
        entity_registry_enabled_default=True,
    ),
    IPFireSensorDescription(
        key="memory_available",
        translation_key="memory_available",
        value_key="memory_available",
        data_group="system",
        device_class=SensorDeviceClass.DATA_SIZE,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfInformation.BYTES,
        suggested_display_precision=1,
        entity_registry_enabled_default=False,
    ),
    IPFireSensorDescription(
        key="memory_free",
        translation_key="memory_free",
        value_key="memory_free",
        data_group="system",
        device_class=SensorDeviceClass.DATA_SIZE,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfInformation.BYTES,
        suggested_display_precision=1,
        entity_registry_enabled_default=False,
    ),
    IPFireSensorDescription(
        key="memory_buffers",
        translation_key="memory_buffers",
        value_key="memory_buffers",
        data_group="system",
        device_class=SensorDeviceClass.DATA_SIZE,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfInformation.BYTES,
        suggested_display_precision=1,
        entity_registry_enabled_default=False,
    ),
    IPFireSensorDescription(
        key="memory_cached",
        translation_key="memory_cached",
        value_key="memory_cached",
        data_group="system",
        device_class=SensorDeviceClass.DATA_SIZE,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfInformation.BYTES,
        suggested_display_precision=1,
        entity_registry_enabled_default=False,
    ),
    IPFireSensorDescription(
        key="disk_root_total",
        translation_key="disk_root_total",
        value_key="disk_root_total",
        data_group="system",
        device_class=SensorDeviceClass.DATA_SIZE,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfInformation.BYTES,
        suggested_display_precision=1,
        entity_registry_enabled_default=False,
    ),
    IPFireSensorDescription(
        key="disk_root_used",
        translation_key="disk_root_used",
        value_key="disk_root_used",
        data_group="system",
        device_class=SensorDeviceClass.DATA_SIZE,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfInformation.BYTES,
        suggested_display_precision=1,
        entity_registry_enabled_default=False,
    ),
    IPFireSensorDescription(
        key="disk_root_available",
        translation_key="disk_root_available",
        value_key="disk_root_available",
        data_group="system",
        device_class=SensorDeviceClass.DATA_SIZE,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfInformation.BYTES,
        suggested_display_precision=1,
        entity_registry_enabled_default=False,
    ),
    IPFireSensorDescription(
        key="disk_root_use_percent",
        translation_key="disk_root_use_percent",
        value_key="disk_root_use_percent",
        data_group="system",
        native_unit_of_measurement="%",
        suggested_display_precision=1,
        entity_registry_enabled_default=True,
    ),
    IPFireSensorDescription(
        key="smart_temperature",
        translation_key="smart_temperature",
        value_key="smart_temperature",
        data_group="system",
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement="°C",
        suggested_display_precision=1,
        entity_registry_enabled_default=True,
    ),
    IPFireSensorDescription(
        key="smart_errors",
        translation_key="smart_errors",
        value_key="smart_errors",
        data_group="system",
        state_class=SensorStateClass.MEASUREMENT,
        entity_registry_enabled_default=False,
    ),
    IPFireSensorDescription(
        key="package_updates",
        translation_key="updates_available",
        value_key="updates_available",
        data_group="system",
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up IPFire sensors."""

    coordinator: IPFireCoordinator = entry.runtime_data.coordinator

    entities: list[SensorEntity] = [
        IPFireTrafficSensor(
            coordinator,
            entry,
            description,
        )
        for description in SENSORS
    ]

    entities.append(IPFireDHCPLeasesSensor(coordinator, entry))

    # The overall Download/Upload sensors represent the RED (WAN) interface.
    # Add separate byte counters for the internal GREEN, ORANGE, and BLUE zones.
    if coordinator.data is not None:
        for zone in ("green", "orange", "blue"):
            interface = coordinator.data.network.interfaces.get(zone)
            if interface is None or interface.device is None:
                continue
            entities.extend(
                IPFireInterfaceTrafficSensor(coordinator, entry, zone, direction)
                for direction in ("rx", "tx")
            )

    async_add_entities(entities)


class IPFireTrafficSensor(
    CoordinatorEntity[IPFireCoordinator],
    SensorEntity,
):
    """Represent an IPFire sensor."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: IPFireCoordinator,
        entry: ConfigEntry,
        description: IPFireSensorDescription,
    ) -> None:
        """Initialize the sensor."""

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
    def native_value(self) -> int | float | str | None:
        """Return the current sensor value."""

        if self.coordinator.data is None:
            return None

        if self.entity_description.data_group == "system":
            data = self.coordinator.data.system
        else:
            data = self.coordinator.data

        value = getattr(data, self.entity_description.value_key, None)

        if self.entity_description.key == "connected_since":
            if value is None:
                return None
            return dt_util.utc_from_timestamp(value)

        return value


class IPFireDHCPLeasesSensor(
    CoordinatorEntity[IPFireCoordinator],
    SensorEntity,
):
    """Report the number of active DHCP leases and expose the lease list."""

    _attr_has_entity_name = True
    _attr_translation_key = "dhcp_active_leases"
    _attr_entity_registry_enabled_default = True
    _attr_state_class = SensorStateClass.MEASUREMENT

    def __init__(
        self,
        coordinator: IPFireCoordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the DHCP lease sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_dhcp_active_leases"
        self._attr_device_info = DeviceInfo(
            identifiers={("ipfire", entry.entry_id)},
            name="IPFire",
            manufacturer="IPFire",
            model="Firewall",
        )

    @property
    def native_value(self) -> int | None:
        """Return the number of active leases."""
        if self.coordinator.data is None:
            return None
        leases = self.coordinator.data.dhcp_leases
        if leases is None:
            return None
        return sum(lease.get("status") == "active" for lease in leases)

    @property
    def extra_state_attributes(self) -> dict[str, list[dict[str, object]]] | None:
        """Expose the lease records as sensor attributes."""
        if self.coordinator.data is None:
            return None
        leases = self.coordinator.data.dhcp_leases
        if leases is None:
            return None
        return {"leases": [dict(lease) for lease in leases]}


class IPFireInterfaceTrafficSensor(
    CoordinatorEntity[IPFireCoordinator],
    SensorEntity,
):
    """Report received or sent bytes for an internal IPFire interface."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: IPFireCoordinator,
        entry: ConfigEntry,
        zone: str,
        direction: str,
    ) -> None:
        """Initialize an internal interface traffic sensor."""
        super().__init__(coordinator)
        self._zone = zone
        self._direction = direction
        key = f"{zone}_{direction}_bytes"
        self.entity_description = SensorEntityDescription(
            key=key,
            translation_key=key,
            device_class=SensorDeviceClass.DATA_SIZE,
            state_class=SensorStateClass.TOTAL_INCREASING,
            native_unit_of_measurement=UnitOfInformation.BYTES,
            suggested_unit_of_measurement=UnitOfInformation.MEGABYTES,
            suggested_display_precision=1,
        )
        self._attr_unique_id = f"{entry.entry_id}_{key}"
        self._attr_device_info = DeviceInfo(
            identifiers={("ipfire", entry.entry_id)},
            name="IPFire",
            manufacturer="IPFire",
            model="Firewall",
        )

    @property
    def native_value(self) -> int | None:
        """Return the current byte counter for the interface."""
        if self.coordinator.data is None:
            return None
        interface = self.coordinator.data.network.interfaces.get(self._zone)
        if interface is None:
            return None
        return getattr(interface, f"{self._direction}_bytes")

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

from .coordinator import IPFireCoordinator


PARALLEL_UPDATES = 0


@dataclass(frozen=True, kw_only=True)
class IPFireSensorDescription(SensorEntityDescription):
    """Describe an IPFire sensor."""

    value_key: str
    data_group: str = "root"


SENSORS: tuple[IPFireSensorDescription, ...] = (
    IPFireSensorDescription(
        key="rxb",
        translation_key="download",
        value_key="rxb",
        device_class=SensorDeviceClass.DATA_SIZE,
        state_class=SensorStateClass.TOTAL_INCREASING,
        native_unit_of_measurement=UnitOfInformation.BYTES,
        suggested_display_precision=1,
    ),
    IPFireSensorDescription(
        key="txb",
        translation_key="upload",
        value_key="txb",
        device_class=SensorDeviceClass.DATA_SIZE,
        state_class=SensorStateClass.TOTAL_INCREASING,
        native_unit_of_measurement=UnitOfInformation.BYTES,
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
        key="connection_state",
        translation_key="connection_state",
        value_key="connection_state",
    ),
    IPFireSensorDescription(
        key="external_ip",
        translation_key="external_ip",
        value_key="external_ip",
    ),
    IPFireSensorDescription(
        key="external_hostname",
        translation_key="external_hostname",
        value_key="external_hostname",
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
    ),
    IPFireSensorDescription(
        key="kernel_version",
        translation_key="kernel_version",
        value_key="kernel_version",
        data_group="system",
    ),
    IPFireSensorDescription(
        key="architecture",
        translation_key="architecture",
        value_key="architecture",
        data_group="system",
    ),
    IPFireSensorDescription(
        key="cpu_model",
        translation_key="cpu_model",
        value_key="cpu_model",
        data_group="system",
    ),
    IPFireSensorDescription(
        key="model",
        translation_key="model",
        value_key="model",
        data_group="system",
    ),
    IPFireSensorDescription(
        key="vendor",
        translation_key="vendor",
        value_key="vendor",
        data_group="system",
    ),
    IPFireSensorDescription(
        key="cpu_count",
        translation_key="cpu_count",
        value_key="cpu_count",
        data_group="system",
    ),
    IPFireSensorDescription(
        key="memory",
        translation_key="memory",
        value_key="memory",
        data_group="system",
        device_class=SensorDeviceClass.DATA_SIZE,
        native_unit_of_measurement=UnitOfInformation.KIBIBYTES,
        suggested_display_precision=1,
    ),
    IPFireSensorDescription(
        key="root_size",
        translation_key="root_size",
        value_key="root_size",
        data_group="system",
        device_class=SensorDeviceClass.DATA_SIZE,
        native_unit_of_measurement=UnitOfInformation.KIBIBYTES,
        suggested_display_precision=1,
    ),
    IPFireSensorDescription(
        key="package_updates",
        translation_key="package_updates",
        value_key="package_updates",
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

    async_add_entities(
        IPFireTrafficSensor(
            coordinator,
            entry,
            description,
        )
        for description in SENSORS
    )


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

        return getattr(data, self.entity_description.value_key, None)

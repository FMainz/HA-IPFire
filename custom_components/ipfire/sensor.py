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

        return getattr(
            self.coordinator.data,
            self.entity_description.value_key,
        )

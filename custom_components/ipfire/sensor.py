from __future__ import annotations

from dataclasses import dataclass

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfDataRate, UnitOfInformation
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import (
    AddEntitiesCallback,
)
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
)

from .const import DATA_COORDINATOR, DOMAIN
from .coordinator import IPFireCoordinator


@dataclass(frozen=True, kw_only=True)
class IPFireSensorDescription(SensorEntityDescription):
    """Describe an IPFire sensor."""

    value_key: str


SENSORS = (
    IPFireSensorDescription(
        key="rxb",
        name="Download",
        value_key="rxb",
        icon="mdi:download-network",
        device_class=SensorDeviceClass.DATA_SIZE,
        state_class=SensorStateClass.TOTAL_INCREASING,
        native_unit_of_measurement=UnitOfInformation.BYTES,
    ),
    IPFireSensorDescription(
        key="txb",
        name="Upload",
        value_key="txb",
        icon="mdi:upload-network",
        device_class=SensorDeviceClass.DATA_SIZE,
        state_class=SensorStateClass.TOTAL_INCREASING,
        native_unit_of_measurement=UnitOfInformation.BYTES,
    ),
    IPFireSensorDescription(
        key="rx_rate",
        name="Download Geschwindigkeit",
        value_key="rx_rate",
        icon="mdi:download-network",
        device_class=SensorDeviceClass.DATA_RATE,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfDataRate.BYTES_PER_SECOND,
        suggested_unit_of_measurement=UnitOfDataRate.KILOBYTES_PER_SECOND,
        suggested_display_precision=1,
    ),
    IPFireSensorDescription(
        key="tx_rate",
        name="Upload Geschwindigkeit",
        value_key="tx_rate",
        icon="mdi:upload-network",
        device_class=SensorDeviceClass.DATA_RATE,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfDataRate.BYTES_PER_SECOND,
        suggested_unit_of_measurement=UnitOfDataRate.KILOBYTES_PER_SECOND,
        suggested_display_precision=1,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up IPFire sensors."""

    coordinator: IPFireCoordinator = (
        hass.data[DOMAIN][entry.entry_id][DATA_COORDINATOR]
    )

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
    """Represent an IPFire traffic sensor."""

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

        self._attr_unique_id = (
            f"{entry.entry_id}_{description.key}"
        )

        self._attr_name = description.name
        self._attr_icon = description.icon

        self._attr_device_class = (
            description.device_class
        )

        self._attr_state_class = (
            description.state_class
        )

        self._attr_native_unit_of_measurement = (
            description.native_unit_of_measurement
        )

        self._attr_suggested_unit_of_measurement = (
            description.suggested_unit_of_measurement
        )

        self._attr_suggested_display_precision = (
            description.suggested_display_precision
        )

        self._attr_device_info = DeviceInfo(
            identifiers={
                (DOMAIN, entry.entry_id)
            },
            name="IPFire",
            manufacturer="IPFire",
            model="Firewall",
        )

    @property
    def native_value(self) -> int | float | None:
        """Return the current sensor value."""

        if not self.coordinator.data:
            return None

        return self.coordinator.data.get(
            self.entity_description.value_key
        )

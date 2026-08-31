from __future__ import annotations

from dataclasses import dataclass

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
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
class IPFireSensorDescription:
    """Describe an IPFire sensor."""

    key: str
    name: str
    icon: str
    device_class: SensorDeviceClass
    state_class: SensorStateClass
    unit: str


SENSORS = (
    IPFireSensorDescription(
        key="rxb",
        name="Download",
        icon="mdi:download-network",
        device_class=SensorDeviceClass.DATA_SIZE,
        state_class=SensorStateClass.TOTAL_INCREASING,
        unit=UnitOfInformation.BYTES,
    ),
    IPFireSensorDescription(
        key="txb",
        name="Upload",
        icon="mdi:upload-network",
        device_class=SensorDeviceClass.DATA_SIZE,
        state_class=SensorStateClass.TOTAL_INCREASING,
        unit=UnitOfInformation.BYTES,
    ),
    IPFireSensorDescription(
        key="rx_rate",
        name="Download Geschwindigkeit",
        icon="mdi:download-network",
        device_class=SensorDeviceClass.DATA_RATE,
        state_class=SensorStateClass.MEASUREMENT,
        unit=UnitOfDataRate.BYTES_PER_SECOND,
    ),
    IPFireSensorDescription(
        key="tx_rate",
        name="Upload Geschwindigkeit",
        icon="mdi:upload-network",
        device_class=SensorDeviceClass.DATA_RATE,
        state_class=SensorStateClass.MEASUREMENT,
        unit=UnitOfDataRate.BYTES_PER_SECOND,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up IPFire sensors."""

    coordinator: IPFireCoordinator = (
        hass.data[DOMAIN][entry.entry_id][
            DATA_COORDINATOR
        ]
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

        self._key = description.key

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
            description.unit
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
            self._key
        )
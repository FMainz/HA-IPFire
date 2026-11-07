from __future__ import annotations

import json
from dataclasses import dataclass

from homeassistant.components import persistent_notification
from homeassistant.components.button import ButtonEntity, ButtonEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import __version__ as HA_VERSION
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.loader import async_get_loaded_integration

from .const import DOMAIN
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
    IPFireButtonDescription(
        key="diagnostic_report",
        translation_key="diagnostic_report",
        icon="mdi:bug-outline",
        entity_category=EntityCategory.DIAGNOSTIC,
        action="diagnostic_report",
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
        IPFireActionButton(
            coordinator,
            entry,
            description,
        )
        for description in BUTTONS
    )


class IPFireActionButton(
    CoordinatorEntity[IPFireCoordinator],
    ButtonEntity,
):
    """Represent an IPFire action button."""

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
        self.entry = entry
        self._attr_unique_id = f"{entry.entry_id}_{description.key}"
        self._attr_device_info = DeviceInfo(
            identifiers={("ipfire", entry.entry_id)},
            name="IPFire",
            manufacturer="IPFire",
            model="Firewall",
        )

    @property
    def available(self) -> bool:
        """Keep the diagnostic report available during coordinator errors."""
        if self.entity_description.action == "diagnostic_report":
            return True
        return super().available

    async def async_press(self) -> None:
        """Handle the button press."""

        if self.entity_description.action == "connect":
            await self.coordinator.async_connect()
        elif self.entity_description.action == "disconnect":
            await self.coordinator.async_disconnect()
        elif self.entity_description.action == "diagnostic_report":
            await self._async_create_diagnostic_report()

    async def _async_create_diagnostic_report(self) -> None:
        """Create a privacy-conscious diagnostic report notification."""
        integration = async_get_loaded_integration(self.hass, DOMAIN)
        integration_version = integration.manifest.get("version", "unknown")
        data = self.coordinator.data
        leases_available = data is not None and data.dhcp_leases is not None
        update_list_available = (
            data is not None and data.available_updates is not None
        )
        update_operation_available = (
            data is not None and data.update_operation is not None
        )
        coordinator_status = (
            "successful" if self.coordinator.last_update_success else "failed"
        )
        data_status = "available" if data is not None else "unavailable"
        leases_status = "available" if leases_available else "unavailable"
        update_list_status = (
            "available" if update_list_available else "unavailable"
        )
        operation_status = (
            "available" if update_operation_available else "unavailable"
        )

        lines = [
            "versions:",
            f"  ha_ipfire: {self._yaml_scalar(integration_version)}",
            f"  home_assistant: {self._yaml_scalar(HA_VERSION)}",
            "connection:",
            f"  coordinator_update: {self._yaml_scalar(coordinator_status)}",
            "  ipfire: "
            f"{self._yaml_scalar(data.connection_state if data else None)}",
            "api_data:",
            f"  last_data: {self._yaml_scalar(data_status)}",
            f"  dhcp_leases: {self._yaml_scalar(leases_status)}",
            f"  available_update_list: {self._yaml_scalar(update_list_status)}",
            f"  update_operation: {self._yaml_scalar(operation_status)}",
            "  api_revision: "
            f"{self._yaml_scalar(data.api_revision if data else None)}",
        ]

        if data is not None:
            lines.extend(
                [
                    "",
                    "ipfire:",
                    f"  version: {self._yaml_scalar(data.system.version)}",
                    "  architecture: "
                    f"{self._yaml_scalar(data.system.architecture)}",
                    "  kernel_version: "
                    f"{self._yaml_scalar(data.system.kernel_version)}",
                ]
            )

            if data.available_updates is not None:
                update_types = sorted(
                    {
                        str(update.get("type", "unknown"))
                        for update in data.available_updates
                    }
                )
                lines.extend(
                    [
                        "",
                        "updates:",
                        f"  count: {len(data.available_updates)}",
                        "  types: "
                        f"{self._yaml_scalar(', '.join(update_types))}",
                    ]
                )

            if data.update_operation is not None:
                status = data.update_operation.get("status", "unknown")
                lines.extend(
                    [
                        "",
                        "update_operation:",
                        f"  status: {self._yaml_scalar(status)}",
                    ]
                )

        report = "\n".join(lines)
        is_german = self.hass.config.language.startswith("de")
        title = (
            "HA-IPFire: Fehlerbericht"
            if is_german
            else "HA-IPFire: Error report"
        )
        notice = (
            "Prüfe den Bericht vor dem Teilen. Er enthält keine Zugangsdaten, "
            "IP-Adressen, Hostnamen oder DHCP-Clientdaten."
            if is_german
            else (
                "Review this report before sharing it. It excludes credentials, "
                "IP addresses, hostnames, and DHCP client details."
            )
        )
        message = f"{notice}\n\n```yaml\n{report}\n```"
        persistent_notification.async_create(
            self.hass,
            message,
            title=title,
            notification_id=f"ipfire_diagnostic_report_{self.entry.entry_id}",
        )

    @staticmethod
    def _yaml_scalar(value: object) -> str:
        """Return a YAML-safe scalar without exposing arbitrary formatting."""
        if value is None:
            return "null"
        if isinstance(value, bool):
            return "true" if value else "false"
        if isinstance(value, (int, float)):
            return str(value)
        return json.dumps(str(value), ensure_ascii=False)

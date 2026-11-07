from __future__ import annotations

import json
import re
from dataclasses import dataclass
from datetime import datetime

from homeassistant.components import persistent_notification
from homeassistant.components.button import ButtonEntity, ButtonEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import __version__ as HA_VERSION
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.loader import async_get_loaded_integration

from .const import (
    CONF_SCAN_INTERVAL,
    CONF_VERIFY_SSL,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
)
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
        coordinator_status = (
            "successful" if self.coordinator.last_update_success else "failed"
        )
        data_status = "available" if data is not None else "unavailable"
        last_error = self.coordinator.last_update_error
        interval = self.entry.options.get(
            CONF_SCAN_INTERVAL,
            DEFAULT_SCAN_INTERVAL,
        )
        entity_counts = self._entity_counts()
        last_error_type, last_error_message = self._safe_error_details(last_error)

        lines = [
            "versions:",
            f"  ha_ipfire: {self._yaml_scalar(integration_version)}",
            f"  home_assistant: {self._yaml_scalar(HA_VERSION)}",
            "settings:",
            f"  scan_interval_seconds: {self._yaml_scalar(interval)}",
            "  verify_ssl_certificate: "
            f"{self._yaml_scalar(self.entry.data.get(CONF_VERIFY_SSL))}",
            "  entities:",
        ]

        for domain, counts in entity_counts.items():
            lines.extend(
                [
                    f"    {domain}:",
                    f"      enabled: {counts['enabled']}",
                    f"      disabled: {counts['disabled']}",
                ]
            )

        lines.extend(
            [
                "connection:",
                "  coordinator_update: "
                f"{self._yaml_scalar(coordinator_status)}",
                "  last_successful_update_utc: "
                f"{self._yaml_scalar(self._format_utc(self.coordinator.last_successful_update_utc))}",
                "  last_error_utc: "
                f"{self._yaml_scalar(self._format_utc(self.coordinator.last_error_utc))}",
                f"  last_error_type: {self._yaml_scalar(last_error_type)}",
                "  last_error_message: "
                f"{self._yaml_scalar(last_error_message)}",
                "  ipfire: "
                f"{self._yaml_scalar(data.connection_state if data else None)}",
                "api_data:",
                f"  last_data: {self._yaml_scalar(data_status)}",
                "  api_revision: "
                f"{self._yaml_scalar(data.api_revision if data else None)}",
            ]
        )

        def unavailable_reason(value: object) -> str | None:
            if value is not None:
                return None
            if data is None:
                return "query_failed" if last_error is not None else "not_queried"
            return "not_reported_by_api"

        leases = data.dhcp_leases if data is not None else None
        updates = data.available_updates if data is not None else None
        operation = data.update_operation if data is not None else None
        lines.extend(
            [
                "  dhcp_leases:",
                "    count: "
                f"{self._yaml_scalar(len(leases) if leases is not None else None)}",
                "    status: "
                f"{self._yaml_scalar('available' if leases is not None else 'unavailable')}",
                f"    reason: {self._yaml_scalar(unavailable_reason(leases))}",
                "  available_update_list:",
                "    count: "
                f"{self._yaml_scalar(len(updates) if updates is not None else None)}",
                "    status: "
                f"{self._yaml_scalar('available' if updates is not None else 'unavailable')}",
                f"    reason: {self._yaml_scalar(unavailable_reason(updates))}",
                "  update_operation:",
                "    status: "
                f"{self._yaml_scalar(self._safe_operation_status(operation))}",
                f"    reason: {self._yaml_scalar(unavailable_reason(operation))}",
            ]
        )

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
                    "  core_update_available: "
                    f"{self._yaml_scalar(data.system.core_update)}",
                    "  package_updates_available: "
                    f"{self._yaml_scalar(data.system.package_updates)}",
                    "  reboot_required: "
                    f"{self._yaml_scalar(data.system.reboot_required)}",
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

    def _entity_counts(self) -> dict[str, dict[str, int]]:
        """Count enabled and disabled entities without including entity IDs."""
        registry = er.async_get(self.hass)
        counts: dict[str, dict[str, int]] = {}
        for entity in er.async_entries_for_config_entry(
            registry,
            self.entry.entry_id,
        ):
            if entity.domain not in {
                "sensor",
                "binary_sensor",
                "button",
                "update",
            }:
                continue
            domain_counts = counts.setdefault(
                entity.domain,
                {"enabled": 0, "disabled": 0},
            )
            key = "disabled" if entity.disabled_by is not None else "enabled"
            domain_counts[key] += 1
        return dict(sorted(counts.items()))

    @staticmethod
    def _format_utc(value: object) -> str | None:
        """Format a timestamp as an ISO 8601 UTC value."""
        return value.isoformat() if isinstance(value, datetime) else None

    @staticmethod
    def _safe_operation_status(
        operation: dict[str, object] | None,
    ) -> str | None:
        """Return only known-safe update operation states."""
        if operation is None:
            return None
        status = operation.get("status")
        if isinstance(status, str) and status in {
            "idle",
            "running",
            "completed",
            "failed",
        }:
            return str(status)
        return "unknown"

    def _safe_error_details(
        self,
        error: BaseException | None,
    ) -> tuple[str | None, str | None]:
        """Redact addresses, hostnames, credentials, and URLs from errors."""
        if error is None:
            return None, None

        message = str(error) or "No error details provided"
        for secret in (
            self.coordinator.base_url,
            self.coordinator.username,
            self.coordinator.password,
        ):
            if secret:
                message = message.replace(secret, "[redacted]")

        message = re.sub(
            r"https?://[^\s'\"]+",
            "[URL redacted]",
            message,
            flags=re.IGNORECASE,
        )
        message = re.sub(
            r"(?i)(host(?:name)?\s+)[^\s,;]+",
            r"\1[redacted]",
            message,
        )
        message = re.sub(
            r"(?i)\b(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+[a-z]{2,}\b",
            "[hostname redacted]",
            message,
        )
        message = re.sub(
            r"\b(?:\d{1,3}\.){3}\d{1,3}\b",
            "[IP address redacted]",
            message,
        )
        message = re.sub(
            r"\b(?:[0-9a-fA-F]{2}[:-]){5}[0-9a-fA-F]{2}\b",
            "[MAC address redacted]",
            message,
        )
        message = re.sub(
            r"(?<![0-9a-fA-F:])(?:[0-9a-fA-F]{0,4}:){2,7}(?:[0-9a-fA-F]{0,4}|(?:\d{1,3}\.){3}\d{1,3})(?![0-9a-fA-F:])",
            "[IP address redacted]",
            message,
        )
        return type(error).__name__, message[:300]

    @staticmethod
    def _yaml_scalar(value: object) -> str:
        """Return a YAML-safe scalar without exposing arbitrary formatting."""
        if value is None:
            return "none"
        if isinstance(value, bool):
            return "yes" if value else "no"
        if isinstance(value, (int, float)):
            return str(value)
        return json.dumps(str(value), ensure_ascii=False)

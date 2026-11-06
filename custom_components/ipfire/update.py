from __future__ import annotations

from typing import Any

from homeassistant.components.update import (
    UpdateEntity,
    UpdateEntityFeature,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .coordinator import IPFireCoordinator


PARALLEL_UPDATES = 1


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the IPFire system update entity."""
    coordinator: IPFireCoordinator = entry.runtime_data.coordinator
    async_add_entities([IPFireSystemUpdateEntity(coordinator, entry)])


class IPFireSystemUpdateEntity(
    CoordinatorEntity[IPFireCoordinator],
    UpdateEntity,
):
    """Represent the complete set of available IPFire updates."""

    _attr_has_entity_name = True
    _attr_translation_key = "system_updates"
    _attr_supported_features = (
        UpdateEntityFeature.INSTALL | UpdateEntityFeature.PROGRESS
    )

    def __init__(
        self,
        coordinator: IPFireCoordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the system update entity."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_system_updates"
        self._attr_device_info = DeviceInfo(
            identifiers={("ipfire", entry.entry_id)},
            name="IPFire",
            manufacturer="IPFire",
            model="Firewall",
        )

    @property
    def available(self) -> bool:
        """Require the API's detailed update list for this entity."""
        return (
            super().available
            and self.coordinator.data is not None
            and self.coordinator.data.available_updates is not None
        )

    @property
    def has_update(self) -> bool:
        """Return whether any core or package updates are pending."""
        updates = self._available_updates
        return updates is not None and bool(updates)

    @property
    def installed_version(self) -> str | None:
        """Return the installed IPFire version."""
        if self.coordinator.data is None:
            return None
        return self.coordinator.data.system.version

    @property
    def latest_version(self) -> str | None:
        """Summarize the batch target; Pakfire installs it as one operation."""
        updates = self._available_updates
        if not updates:
            return None

        core_update = next(
            (update for update in updates if update.get("type") == "core"),
            None,
        )
        package_count = sum(
            update.get("type") == "package" for update in updates
        )

        parts = []
        if core_update is not None:
            parts.append(f"Core {core_update.get('available_release')}")
        if package_count:
            parts.append(
                f"{package_count} package update"
                f"{'s' if package_count != 1 else ''}"
            )
        return " + ".join(parts)

    @property
    def release_summary(self) -> str | None:
        """List the packages and versions included in the update batch."""
        updates = self._available_updates
        if updates is None:
            return None

        lines = []
        for update in updates:
            if update.get("type") == "core":
                lines.append(
                    "Core update: release "
                    f"{update.get('installed_release')} → "
                    f"{update.get('available_release')}"
                )
                continue

            name = update.get("name", "Unknown package")
            installed = update.get("installed_version", "?")
            available = update.get("available_version", "?")
            lines.append(f"{name}: {installed} → {available}")

        summary = "\n".join(lines)
        return summary[:255]

    @property
    def in_progress(self) -> bool:
        """Report when Pakfire is currently installing the update batch."""
        if self.coordinator.data is None:
            return False
        operation = self.coordinator.data.update_operation or {}
        return operation.get("status") in {"starting", "running"}

    async def async_install(
        self,
        version: str | None,
        backup: bool,
        **kwargs: Any,
    ) -> None:
        """Start Pakfire's all-updates upgrade through the IPFire API."""
        await self.coordinator.async_start_upgrade()

    @property
    def _available_updates(self) -> tuple[dict[str, object], ...] | None:
        """Return the API-reported update batch, if available."""
        if self.coordinator.data is None:
            return None
        return self.coordinator.data.available_updates

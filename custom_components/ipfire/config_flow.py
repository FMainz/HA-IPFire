from __future__ import annotations

from typing import Any

import aiohttp
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.config_entries import (
    ConfigFlowResult,
    OptionsFlowWithReload,
)
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.aiohttp_client import (
    async_get_clientsession,
)

from .const import (
    CONF_PASSWORD,
    CONF_SCAN_INTERVAL,
    CONF_URL,
    CONF_USERNAME,
    CONF_VERIFY_SSL,
    DEFAULT_SCAN_INTERVAL,
    DEFAULT_URL,
    DOMAIN,
    MAX_SCAN_INTERVAL,
    MIN_SCAN_INTERVAL,
    API_PATH,
)


async def validate_input(
    hass: HomeAssistant,
    data: dict[str, Any],
) -> None:
    """Validate the IPFire configuration."""

    url = (
        data[CONF_URL].rstrip("/")
        + API_PATH
    )

    session = async_get_clientsession(hass)

    try:
        async with session.get(
            url,
            auth=aiohttp.BasicAuth(
                data[CONF_USERNAME],
                data[CONF_PASSWORD],
            ),
            ssl=data[CONF_VERIFY_SSL],
            timeout=aiohttp.ClientTimeout(total=10),
        ) as response:
            if response.status in (401, 403):
                raise InvalidAuth

            response.raise_for_status()

            payload = await response.json(content_type=None)

    except InvalidAuth:
        raise

    except (aiohttp.ClientError, TimeoutError) as err:
        raise CannotConnect from err

    except (ValueError, TypeError) as err:
        raise InvalidResponse from err

    if not isinstance(payload, dict):
        raise InvalidResponse

    if payload.get("api_version") != 1:
        raise InvalidResponse

    connection = payload.get("connection")
    traffic = payload.get("traffic")

    if not isinstance(connection, dict):
        raise InvalidResponse

    if not isinstance(traffic, dict):
        raise InvalidResponse

    if "rx_bytes" not in traffic:
        raise InvalidResponse

    if "tx_bytes" not in traffic:
        raise InvalidResponse


def scan_interval_schema(
    default: int,
) -> vol.Schema:
    """Return the schema for the scan interval."""

    return vol.Schema(
        {
            vol.Required(
                CONF_SCAN_INTERVAL,
                default=default,
            ): vol.All(
                vol.Coerce(int),
                vol.Range(
                    min=MIN_SCAN_INTERVAL,
                    max=MAX_SCAN_INTERVAL,
                ),
            )
        }
    )


def connection_schema(
    suggested: dict[str, Any] | None = None,
) -> vol.Schema:
    """Return the connection schema."""

    suggested = suggested or {}

    return vol.Schema(
        {
            vol.Required(
                CONF_URL,
                default=suggested.get(
                    CONF_URL,
                    DEFAULT_URL,
                ),
            ): str,
            vol.Required(
                CONF_USERNAME,
                default=suggested.get(
                    CONF_USERNAME,
                    "",
                ),
            ): str,
            vol.Required(
                CONF_PASSWORD,
            ): str,
            vol.Optional(
                CONF_VERIFY_SSL,
                default=suggested.get(
                    CONF_VERIFY_SSL,
                    False,
                ),
            ): bool,
        }
    )


class ConfigFlow(
    config_entries.ConfigFlow,
    domain=DOMAIN,
):
    """Handle an IPFire config flow."""

    VERSION = 2

    async def async_step_user(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> ConfigFlowResult:
        """Handle the initial setup."""

        errors: dict[str, str] = {}

        if user_input is not None:
            url = user_input[CONF_URL].rstrip("/")

            if any(
                entry.data.get(CONF_URL, "").rstrip("/")
                == url
                for entry in self.hass.config_entries.async_entries(
                    DOMAIN
                )
            ):
                return self.async_abort(
                    reason="already_configured"
                )

            try:
                await validate_input(
                    self.hass,
                    user_input,
                )

            except InvalidAuth:
                errors["base"] = "invalid_auth"

            except CannotConnect:
                errors["base"] = "cannot_connect"

            except InvalidResponse:
                errors["base"] = "invalid_response"

            except Exception:
                errors["base"] = "unknown"

            else:
                return self.async_create_entry(
                    title=url,
                    data={
                        CONF_URL: url,
                        CONF_USERNAME: user_input[
                            CONF_USERNAME
                        ],
                        CONF_PASSWORD: user_input[
                            CONF_PASSWORD
                        ],
                        CONF_VERIFY_SSL: user_input[
                            CONF_VERIFY_SSL
                        ],
                    },
                    options={
                        CONF_SCAN_INTERVAL: user_input.get(
                            CONF_SCAN_INTERVAL,
                            DEFAULT_SCAN_INTERVAL,
                        )
                    },
                )

        schema = connection_schema()

        schema = vol.All(
            schema,
            vol.Schema(
                {
                    vol.Required(
                        CONF_SCAN_INTERVAL,
                        default=DEFAULT_SCAN_INTERVAL,
                    ): vol.All(
                        vol.Coerce(int),
                        vol.Range(
                            min=MIN_SCAN_INTERVAL,
                            max=MAX_SCAN_INTERVAL,
                        ),
                    )
                }
            ),
        )

        return self.async_show_form(
            step_id="user",
            data_schema=schema,
            errors=errors,
        )

    async def async_step_reconfigure(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> ConfigFlowResult:
        """Handle reconfiguration."""

        entry = self._get_reconfigure_entry()
        errors: dict[str, str] = {}

        if user_input is not None:
            url = user_input[CONF_URL].rstrip("/")

            if any(
                existing.entry_id != entry.entry_id
                and existing.data.get(
                    CONF_URL,
                    "",
                ).rstrip("/")
                == url
                for existing in self.hass.config_entries.async_entries(
                    DOMAIN
                )
            ):
                errors["base"] = "already_configured"
            else:
                try:
                    await validate_input(
                        self.hass,
                        user_input,
                    )

                except InvalidAuth:
                    errors["base"] = "invalid_auth"

                except CannotConnect:
                    errors["base"] = "cannot_connect"

                except InvalidResponse:
                    errors["base"] = "invalid_response"

                except Exception:
                    errors["base"] = "unknown"

                else:
                    return self.async_update_reload_and_abort(
                        entry,
                        title=url,
                        data_updates={
                            CONF_URL: url,
                            CONF_USERNAME: user_input[
                                CONF_USERNAME
                            ],
                            CONF_PASSWORD: user_input[
                                CONF_PASSWORD
                            ],
                            CONF_VERIFY_SSL: user_input[
                                CONF_VERIFY_SSL
                            ],
                        },
                    )

        return self.async_show_form(
            step_id="reconfigure",
            data_schema=self.add_suggested_values_to_schema(
                connection_schema(),
                entry.data,
            ),
            errors=errors,
        )

    async def async_step_reauth(
        self,
        entry_data: dict[str, Any],
    ) -> ConfigFlowResult:
        """Handle reauthentication."""

        return await self.async_step_reauth_confirm()

    async def async_step_reauth_confirm(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> ConfigFlowResult:
        """Confirm reauthentication."""

        entry = self._get_reauth_entry()
        errors: dict[str, str] = {}

        if user_input is not None:
            data = dict(entry.data)
            data.update(
                {
                    CONF_USERNAME: user_input[
                        CONF_USERNAME
                    ],
                    CONF_PASSWORD: user_input[
                        CONF_PASSWORD
                    ],
                }
            )

            try:
                await validate_input(
                    self.hass,
                    data,
                )

            except InvalidAuth:
                errors["base"] = "invalid_auth"

            except CannotConnect:
                errors["base"] = "cannot_connect"

            except InvalidResponse:
                errors["base"] = "invalid_response"

            except Exception:
                errors["base"] = "unknown"

            else:
                return self.async_update_reload_and_abort(
                    entry,
                    data_updates={
                        CONF_USERNAME: data[
                            CONF_USERNAME
                        ],
                        CONF_PASSWORD: data[
                            CONF_PASSWORD
                        ],
                    },
                )

        return self.async_show_form(
            step_id="reauth_confirm",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_USERNAME,
                        default=entry.data[
                            CONF_USERNAME
                        ],
                    ): str,
                    vol.Required(
                        CONF_PASSWORD,
                    ): str,
                }
            ),
            errors=errors,
        )

    @staticmethod
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> OptionsFlowWithReload:
        """Return the options flow."""

        return OptionsFlowHandler()


class OptionsFlowHandler(OptionsFlowWithReload):
    """Handle IPFire options."""

    async def async_step_init(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> ConfigFlowResult:
        """Manage IPFire options."""

        if user_input is not None:
            return self.async_create_entry(
                title="",
                data=user_input,
            )

        current_interval = self.config_entry.options.get(
            CONF_SCAN_INTERVAL,
            self.config_entry.data.get(
                CONF_SCAN_INTERVAL,
                DEFAULT_SCAN_INTERVAL,
            ),
        )

        return self.async_show_form(
            step_id="init",
            data_schema=scan_interval_schema(
                current_interval
            ),
        )


class InvalidAuth(HomeAssistantError):
    """Invalid IPFire credentials."""


class CannotConnect(HomeAssistantError):
    """Unable to connect to IPFire."""


class InvalidResponse(HomeAssistantError):
    """Invalid response from IPFire."""

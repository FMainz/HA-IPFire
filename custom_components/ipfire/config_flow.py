from __future__ import annotations

import aiohttp
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError

from .const import (
    CONF_PASSWORD,
    CONF_URL,
    CONF_USERNAME,
    CONF_VERIFY_SSL,
    DEFAULT_URL,
    DOMAIN,
    SPEED_PATH,
)


async def validate_input(
    hass: HomeAssistant,
    data: dict,
) -> None:
    """Validate the IPFire configuration."""

    url = (
        data[CONF_URL].rstrip("/")
        + SPEED_PATH
    )

    timeout = aiohttp.ClientTimeout(
        total=10
    )

    connector = aiohttp.TCPConnector(
        ssl=data[CONF_VERIFY_SSL]
    )

    async with aiohttp.ClientSession(
        connector=connector,
        timeout=timeout,
    ) as session:

        try:
            async with session.get(
                url,
                auth=aiohttp.BasicAuth(
                    data[CONF_USERNAME],
                    data[CONF_PASSWORD],
                ),
            ) as response:

                if response.status in (
                    401,
                    403,
                ):
                    raise InvalidAuth

                response.raise_for_status()

                await response.read()

        except InvalidAuth:
            raise

        except (
            aiohttp.ClientError,
            TimeoutError,
        ) as err:
            raise CannotConnect from err


class ConfigFlow(
    config_entries.ConfigFlow,
    domain=DOMAIN,
):
    """Handle an IPFire config flow."""

    VERSION = 1

    async def async_step_user(
        self,
        user_input: dict | None = None,
    ) -> config_entries.FlowResult:
        """Handle the initial setup."""

        errors: dict[str, str] = {}

        if user_input is not None:

            try:
                await validate_input(
                    self.hass,
                    user_input,
                )

            except InvalidAuth:
                errors["base"] = "invalid_auth"

            except CannotConnect:
                errors["base"] = "cannot_connect"

            except Exception:
                errors["base"] = "unknown"

            else:
                await self.async_set_unique_id(
                    user_input[CONF_URL]
                    .rstrip("/")
                    .lower()
                )

                self._abort_if_unique_id_configured()

                return self.async_create_entry(
                    title=user_input[CONF_URL]
                    .rstrip("/"),
                    data=user_input,
                )

        schema = vol.Schema(
            {
                vol.Required(
                    CONF_URL,
                    default=DEFAULT_URL,
                ): str,

                vol.Required(
                    CONF_USERNAME,
                ): str,

                vol.Required(
                    CONF_PASSWORD,
                ): str,

                vol.Optional(
                    CONF_VERIFY_SSL,
                    default=False,
                ): bool,
            }
        )

        return self.async_show_form(
            step_id="user",
            data_schema=schema,
            errors=errors,
        )


class InvalidAuth(HomeAssistantError):
    """Invalid IPFire credentials."""


class CannotConnect(HomeAssistantError):
    """Unable to connect to IPFire."""
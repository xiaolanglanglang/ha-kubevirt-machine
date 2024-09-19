from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
import voluptuous as vol

from . import const


class HAKubevirtMachineConfigFlow(config_entries.ConfigFlow, domain=const.DOMAIN):
    """处理 HAKubevirtMachine 配置流程。"""

    VERSION = 1

    async def async_step_user(self, user_input=None) -> FlowResult:
        """处理用户输入的配置。"""
        errors = {}
        if user_input is not None:
            # 所有配置项都必填
            if not user_input.get(const.CONF_API_URL):
                errors["base"] = "api_url_required"
            elif not user_input.get(const.CONF_API_CA_CERT):
                errors["base"] = "api_ca_cert_required"
            elif not user_input.get(const.CONF_API_TOKEN):
                errors["base"] = "api_token_required"
            elif not user_input.get(const.CONF_NAMESPACE):
                errors["base"] = "namespace_required"
            if not errors:
                return self.async_create_entry(title="Kubevirt 虚拟机管理", data=user_input)

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(const.CONF_API_URL): str,
                    vol.Required(const.CONF_API_TOKEN): str,
                    vol.Required(const.CONF_API_CA_CERT): str,
                    vol.Required(const.CONF_NAMESPACE): str,
                }
            ),
            errors=errors,
        )

import logging
from datetime import timedelta

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.exceptions import ConfigEntryAuthFailed

from .const import DOMAIN, CONF_API_URL, CONF_API_TOKEN, CONF_API_CA_CERT, CONF_NAMESPACE
from .kubevirt_api import KubevirtAPI

_LOGGER = logging.getLogger(__name__)


class KubevirtDataUpdateCoordinator(DataUpdateCoordinator):
    """用于管理 Kubevirt 数据的协调器类。"""

    def __init__(self, hass: HomeAssistant, entry):
        """初始化协调器。"""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=30),
        )
        self.api = KubevirtAPI(
            entry.data[CONF_API_URL],
            entry.data[CONF_API_TOKEN],
            entry.data[CONF_API_CA_CERT],
            entry.data[CONF_NAMESPACE]
        )

    async def _async_update_data(self):
        """获取最新的虚拟机数据。"""
        try:
            return await self.hass.async_add_executor_job(self.api.get_vms)
        except Exception as err:
            raise ConfigEntryAuthFailed("无法连接到 Kubevirt API") from err

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, STATE_ON, STATE_OFF
from .coordinator import KubevirtDataUpdateCoordinator


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    """设置 Kubevirt 虚拟机开关实体。"""
    coordinator = hass.data[DOMAIN][entry.entry_id]

    async_add_entities(
        KubevirtVMSwitch(coordinator, vm_name)
        for vm_name in coordinator.data
    )


class KubevirtVMSwitch(CoordinatorEntity, SwitchEntity):
    """代表 Kubevirt 虚拟机的开关实体。"""

    def __init__(self, coordinator: KubevirtDataUpdateCoordinator, vm_name: str):
        """初始化 Kubevirt 虚拟机开关。"""
        super().__init__(coordinator)
        self._vm_name = vm_name
        self._attr_unique_id = f"{DOMAIN}_{vm_name}"
        self._attr_name = f"Kubevirt VM {vm_name}"

    @property
    def is_on(self) -> bool:
        """返回虚拟机是否正在运行。"""
        return self.coordinator.data[self._vm_name]['state'] == STATE_ON

    @property
    def available(self) -> bool:
        """返回虚拟机是否可用。"""
        return self._vm_name in self.coordinator.data

    async def async_turn_on(self, **kwargs) -> None:
        """启动虚拟机。"""
        self.coordinator.data[self._vm_name]['state'] = STATE_ON
        await self.hass.async_add_executor_job(self.coordinator.api.start_vm, self._vm_name)
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs) -> None:
        """关闭虚拟机。"""
        self.coordinator.data[self._vm_name]['state'] = STATE_OFF
        await self.hass.async_add_executor_job(self.coordinator.api.stop_vm, self._vm_name)
        await self.coordinator.async_request_refresh()

    @property
    def extra_state_attributes(self):
        """返回虚拟机的额外属性。"""
        if self._vm_name not in self.coordinator.data:
            return {}
        vm_data = self.coordinator.data[self._vm_name]
        return {"status": vm_data['status']}

import logging
import requests
from requests.exceptions import RequestException
import tempfile
import os

from .const import STATE_ON, STATE_OFF, STATE_UNKNOWN

_LOGGER = logging.getLogger(__name__)


class KubevirtAPI:
    """用于与 Kubevirt API 交互的类。"""

    def __init__(self, api_url, api_token, api_ca_cert, namespace):
        """初始化 KubevirtAPI。"""
        self.api_url = api_url
        self.api_token = api_token
        self.api_ca_cert = api_ca_cert
        self.namespace = namespace
        self.headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json"
        }
        self.ca_cert_file = self._create_temp_ca_cert_file()

    def _create_temp_ca_cert_file(self):
        """创建临时CA证书文件。"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as temp_file:
            # 添加换行符
            cert_content = self.api_ca_cert.replace(
                "-----BEGIN CERTIFICATE-----", "-----BEGIN CERTIFICATE-----\n")
            cert_content = cert_content.replace(
                "-----END CERTIFICATE-----", "\n-----END CERTIFICATE-----")
            temp_file.write(cert_content)
            return temp_file.name

    def get_vms(self):
        """获取虚拟机列表及其状态。"""
        try:
            url = f"{
                self.api_url}/apis/kubevirt.io/v1/namespaces/{self.namespace}/virtualmachines"
            response = requests.get(
                url, headers=self.headers, verify=self.ca_cert_file, timeout=10)
            response.raise_for_status()
            vms = response.json()

            vm_states = {}
            for vm in vms['items']:
                name = vm['metadata']['name']
                status = vm['status'].get('printableStatus', STATE_UNKNOWN)
                if status in ['Running', 'Starting']:
                    state = STATE_ON
                elif status in ['Stopped', 'Succeeded', 'Stopping']:
                    state = STATE_OFF
                else:
                    state = STATE_UNKNOWN

                vm_states[name] = {
                    'state': state,
                    'status': status
                }

            return vm_states
        except RequestException as e:
            _LOGGER.error(f"获取虚拟机列表时出错: {e}")
            return {}

    def start_vm(self, vm_name):
        """启动虚拟机。"""
        try:
            url = f"{self.api_url}/apis/subresources.kubevirt.io/v1/namespaces/{
                self.namespace}/virtualmachines/{vm_name}/start"
            response = requests.put(
                url, headers=self.headers, verify=self.ca_cert_file, timeout=10)
            response.raise_for_status()
            return True
        except RequestException as e:
            _LOGGER.error(f"启动虚拟机 {vm_name} 时出错: {e}")
            return False

    def stop_vm(self, vm_name):
        """停止虚拟机。"""
        try:
            url = f"{self.api_url}/apis/subresources.kubevirt.io/v1/namespaces/{
                self.namespace}/virtualmachines/{vm_name}/stop"
            response = requests.put(
                url, headers=self.headers, verify=self.ca_cert_file, timeout=10)
            response.raise_for_status()
            return True
        except RequestException as e:
            _LOGGER.error(f"停止虚拟机 {vm_name} 时出错: {e}")
            return False

    def restart_vm(self, vm_name):
        """重启虚拟机。"""
        if self.stop_vm(vm_name):
            return self.start_vm(vm_name)
        return False

    def __del__(self):
        """清理临时CA证书文件。"""
        if hasattr(self, 'ca_cert_file') and os.path.exists(self.ca_cert_file):
            os.remove(self.ca_cert_file)

import json
from exhibition.base import *
from exhibition.selector.types.abstract import ExecutableAbstract


class Shadowsocks(ExecutableAbstract):
    EXECUTABLE_TYPE = ExecutableEnum.SHADOWSOCKS
    SUPPORT_INPUT = {
        ProxyEnum.SOCKS5,
    }
    SUPPORT_OUTPUT = {
        ProxyEnum.SHADOWSOCKS,
    }

    def config_filename(self, name: str) -> str:
        return f'{name}.json'

    def process_args(self, config_path: str) -> list[str]:
        return [self.executable.path, '-c', config_path, ]

    def export_config(
            self,
            export_settings: ExportSettings,
            working_settings: list[tuple[WorkingNodeState, WorkingNodeSettings]],
    ) -> str:
        raise NotImplementedError

    def working_config(
            self,
            statue: WorkingNodeState,
            settings: WorkingNodeSettings,
    ):
        config = settings.origin.copy()
        config |= {
            'remarks': settings.id,
            'local_address': statue.host,
            'local_port': statue.port,
        }
        if plugin := config.get('plugin') and not self.executable.obfs_plugin:
            raise ValueError(f'节点需要使用插件"{plugin}", 系统中未找到插件')
        return json.dumps(config, indent=2)

import abc
from exhibition.base import *


class ExecutableAbstract(abc.ABC):
    EXECUTABLE_TYPE: ExecutableEnum = None
    SUPPORT_INPUT = {}
    SUPPORT_OUTPUT = {}


    def __init__(self, executable: Executable):
        self.executable = executable

    def process_args(self, config_path: str) -> list[str]:
        raise NotImplementedError

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
    ) -> str:
        raise NotImplementedError

    def convert_custom_config(self, settings: CustomNodeSettings) -> WorkingNodeSettings:
        raise NotImplementedError

    def config_filename(self, name: str) -> str:
        raise NotImplementedError


__all__ = [
    'ExecutableAbstract',
]

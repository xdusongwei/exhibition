from exhibition.base import *
from exhibition.selector.types.abstract import ExecutableAbstract
from exhibition.selector.types.v2ray import V2Ray
from exhibition.selector.types.shadowsocks import Shadowsocks
from exhibition.selector.types.xray import XRay


class Selector:
    @classmethod
    def working_node(cls, executables: list[Executable], settings: WorkingNodeSettings) -> None | ExecutableAbstract:
        executable = cls._query_one_executable(executables, ProxyEnum.SOCKS5, settings.proxy)
        return executable

    @classmethod
    def export_node(cls, executables: list[Executable], settings: ExportSettings) -> None | ExecutableAbstract:
        executable = cls._query_one_executable(executables, settings.proxy, ProxyEnum.SOCKS5)
        return executable

    @classmethod
    def _query_all_executables(cls, executables: list[Executable], i: ProxyEnum, o: ProxyEnum) -> list[ExecutableAbstract]:
        types: list = [
            XRay,
            V2Ray,
            Shadowsocks,
        ]
        result = list()
        for t in types:
            if i not in t.SUPPORT_INPUT or o not in t.SUPPORT_OUTPUT:
                continue
            proxy = t.EXECUTABLE_TYPE
            for executable in executables:
                if executable.type != proxy:
                    continue
                instance: ExecutableAbstract = t(executable=executable)
                result.append(instance)
        return result

    @classmethod
    def _query_one_executable(cls, executables: list[Executable], i: ProxyEnum, o: ProxyEnum) -> None | ExecutableAbstract:
        executables = cls._query_all_executables(executables, i, o)
        return executables[0] if executables else None


__all__ = [
    'Selector',
    'ExecutableAbstract',
]

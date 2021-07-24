import abc
import enum
from dataclasses import dataclass, field
import base58
import xxhash


def generate_hash(prefix=None, *args) -> str:
    text = xxhash.xxh3_64('&'.join(args)).hexdigest()
    h = base58.b58encode(text).decode()[-8:]
    prefix = prefix or ''
    return f'{prefix}{h}'


class WrapEnum(enum.Enum):
    WEBSOCKET = enum.auto()
    HTTP2 = enum.auto()
    GRPC = enum.auto()


class ExecutableEnum(enum.Enum):
    SHADOWSOCKS = enum.auto()
    V2RAY = enum.auto()


@dataclass
class Executable:
    path: str
    type: ExecutableEnum = field(default=None)
    version: str = field(default=None)
    obfs_plugin: str = field(default=None)

    def __str__(self) -> str:
        return f'<Executable {self.type} Ver:{self.version} Path:{self.path}>'

    def __repr__(self) -> str:
        return self.__str__()

    def to_dict(self):
        return {
            'type': self.type.name if self.type else None,
            'version': self.version,
            'path': self.path,
            'obfsPlugin': self.obfs_plugin,
        }


class ProxyEnum(enum.Enum):
    SHADOWSOCKS = enum.auto()
    VMESS = enum.auto()
    SOCK5 = enum.auto()
    HTTP = enum.auto()
    HTTPS = enum.auto()

    def query_all(self, executables: list[Executable]) -> list[Executable]:
        filter_set = set()
        match self:
            case ProxyEnum.SHADOWSOCKS:
                filter_set = {ExecutableEnum.SHADOWSOCKS, }
            case ProxyEnum.VMESS | ProxyEnum.SOCK5 | ProxyEnum.HTTP | ProxyEnum.HTTPS:
                filter_set = {ExecutableEnum.V2RAY, }
            case _:
                return list()
        return [executable for executable in executables if executable.type in filter_set]

    def query_one(self, executables: list[Executable]) -> None | Executable:
        executables = self.query_all(executables=executables)
        return executables[0] if executables else None

class StreamEnum(enum.Enum):
    STDOUT = enum.auto()
    STDERR = enum.auto()


class ObfuscatingEnum(enum.Enum):
    WEBSOCKET = enum.auto()


class ActionEnum(enum.Enum):
    NODE_SHUTDOWN = enum.auto()
    EXECUTABLE_CHANGED = enum.auto()
    EXECUTABLE_REFRESH = enum.auto()
    EXECUTABLE_UPDATED = enum.auto()
    PROCESS_STARTED = enum.auto()
    PROCESS_TEXT = enum.auto()
    PROCESS_EOF = enum.auto()
    # 故意触发 Process 对象的 stop()
    PROCESS_STOPPED = enum.auto()
    AIRPORT_SUBSCRIBE = enum.auto()
    AIRPORT_UPDATED = enum.auto()
    AIRPORT_REMOVE = enum.auto()
    NODE_LATENCY_TEST = enum.auto()
    EXPORT_BOOT = enum.auto()
    EXPORT_REFRESH = enum.auto()
    STORE_UPDATED = enum.auto()
    STORE_STOP_NODES = enum.auto()
    STORE_SORT_NODES = enum.auto()
    STORE_START_NODES = enum.auto()


@dataclass
class NodeSettings(abc.ABC):
    id: str
    name: str
    proxy: ProxyEnum
    host: str
    port: int
    tls: bool
    origin: dict
    chiper: str = field(default=None)
    alter_id: str = field(default=None)
    uuid: str = field(default=None)
    wrap: WrapEnum = field(default=None)
    airport_id: str = field(default=None)

    @classmethod
    def generate_hash(cls, name, host, port) -> str:
        return generate_hash('NS', str(name), str(host), str(port))

    def __str__(self) -> str:
        return f'<NodeSettings name:{self.name} host:{self.host}> port:{self.port}'

    def __repr__(self) -> str:
        return self.__str__()


@dataclass
class AirportSettings:
    id: str
    name: str
    url: str


@dataclass
class ExportSettings:
    id: str
    name: str
    proxy: ProxyEnum
    host: str
    port: int
    obfuscating: ObfuscatingEnum = field(default=None)
    path: str = field(default=None)
    alter_id: int = field(default=None)
    uuid: str = field(default=None)


__all__ = [
    'generate_hash',
    'WrapEnum',
    'ExecutableEnum',
    'Executable',
    'ProxyEnum',
    'StreamEnum',
    'ObfuscatingEnum',
    'ActionEnum',
    'NodeSettings',
    'AirportSettings',
    'ExportSettings',
]
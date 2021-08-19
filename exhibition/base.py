import enum
from dataclasses import dataclass, field
from datetime import datetime
import base58
import xxhash


def generate_hash(prefix=None, *args) -> str:
    text = xxhash.xxh3_64('&'.join(args)).hexdigest()
    h = base58.b58encode(text).decode()[-8:]
    prefix = prefix or ''
    return f'{prefix}{h}'


def timestamp() -> int:
    return int(1000 * datetime.now().timestamp())


class WrapEnum(enum.Enum):
    WEBSOCKET = enum.auto()
    HTTP2 = enum.auto()
    GRPC = enum.auto()


class ExecutableEnum(enum.Enum):
    SHADOWSOCKS = enum.auto()
    V2RAY = enum.auto()
    XRAY = enum.auto()


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
    VLESS = enum.auto()
    TROJAN = enum.auto()
    SOCK5 = enum.auto()
    HTTP = enum.auto()
    HTTPS = enum.auto()


class StreamEnum(enum.Enum):
    STDOUT = enum.auto()
    STDERR = enum.auto()


class ObfuscatingEnum(enum.Enum):
    WEBSOCKET = enum.auto()
    HTTP2 = enum.auto()


class ActionEnum(enum.Enum):
    NODE_SHUTDOWN = enum.auto()
    PROCESS_STARTED = enum.auto()
    PROCESS_TEXT = enum.auto()
    PROCESS_EOF = enum.auto()
    # 故意触发 Process 对象的 stop()
    PROCESS_STOPPED = enum.auto()
    EXECUTABLE_CHANGED = enum.auto()
    EXECUTABLE_REFRESH = enum.auto()
    EXECUTABLE_UPDATED = enum.auto()
    AIRPORT_SUBSCRIBE = enum.auto()
    AIRPORT_UPDATED = enum.auto()
    AIRPORT_REMOVE = enum.auto()
    WORKING_LATENCY_TEST = enum.auto()
    EXPORT_BOOT = enum.auto()
    EXPORT_REFRESH = enum.auto()
    EXPORT_UPDATE = enum.auto()
    EXPORT_REMOVE = enum.auto()
    STORE_UPDATED = enum.auto()
    STORE_STOP_NODES = enum.auto()
    STORE_SORT_NODES = enum.auto()
    STORE_START_NODES = enum.auto()
    STORE_SAVE_SETTINGS = enum.auto()
    CUSTOM_NODE_UPDATED = enum.auto()
    CUSTOM_NODE_REMOVE = enum.auto()


@dataclass
class BaseNodeSettings:
    id: str
    name: str
    proxy: ProxyEnum
    host: str
    port: int
    user: str = field(default=None)
    password: str = field(default=None)
    obfuscating: ObfuscatingEnum = field(default=None)
    tls: str = field(default=None)
    path: str = field(default=None)
    alter_id: int = field(default=None)
    uuid: str = field(default=None)
    security: str = field(default=None)
    usage: str = field(default=None)
    key_file: str = field(default=None)
    certificate_file: str = field(default=None)
    encryption: str = field(default=None)
    flow: str = field(default=None)
    encrypt_method: str = field(default=None)


@dataclass
class CustomNodeSettings(BaseNodeSettings):
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'proxy': self.proxy.name,
            'host': self.host,
            'port': self.port,
            'obfuscating': self.obfuscating.name if self.obfuscating else None,
            'path': self.path,
            'alterId': self.alter_id,
            'uuid': self.uuid,
            'security': self.security,
            'encryption': self.encryption,
            'flow': self.flow,
            'encryptMethod': self.encrypt_method,
        }


@dataclass
class WorkingNodeSettings(BaseNodeSettings):
    airport_id: str = field(default=None)
    origin: dict = field(default=None)

    @classmethod
    def from_custom_node(cls, settings: CustomNodeSettings) -> 'WorkingNodeSettings':
        name = settings.name
        proxy = settings.proxy
        host = settings.host
        port = settings.port
        return WorkingNodeSettings(
            id=settings.id,
            name=name,
            host=host,
            port=port,
            proxy=proxy,
            obfuscating=settings.obfuscating,
            tls=settings.tls,
            path=settings.path,
            alter_id=settings.alter_id,
            uuid=settings.uuid,
            security=settings.security,
            encryption=settings.encryption,
            flow=settings.flow,
            encrypt_method=settings.encrypt_method,
        )

    @classmethod
    def from_subscribe(cls, proxy: ProxyEnum, origin: dict) -> 'WorkingNodeSettings':
        match proxy:
            case ProxyEnum.SHADOWSOCKS:
                name = origin['remarks']
                host = origin['server']
                port = origin['server_port']
                node_hash = WorkingNodeSettings.generate_hash(name, host, port, proxy)
                settings = WorkingNodeSettings(
                    id=node_hash,
                    name=name,
                    proxy=ProxyEnum.SHADOWSOCKS,
                    host=host,
                    port=port,
                    origin=origin,
                )
            case ProxyEnum.VMESS:
                name = origin['ps']
                host = origin['add']
                port = origin['port']
                alter_id = origin.get('aid')
                uuid = str(origin.get('id')) if origin.get('id') else None
                node_hash = WorkingNodeSettings.generate_hash(name, host, port, proxy)
                settings = WorkingNodeSettings(
                    id=node_hash,
                    name=name,
                    proxy=ProxyEnum.VMESS,
                    host=host,
                    port=port,
                    alter_id=alter_id,
                    uuid=uuid,
                    origin=origin,
                )
            case _:
                raise ValueError(f'无法处理的订阅代理设置: {origin}')
        return settings

    @classmethod
    def generate_hash(cls, name, host, port, proxy: ProxyEnum) -> str:
        return generate_hash('NA', str(name), str(host), str(port), proxy.name)

    def __str__(self) -> str:
        return f'<WorkingNodeSettings name:"{self.name}" {self.proxy.name}://{self.host}:{self.port} >'

    def __repr__(self) -> str:
        return self.__str__()


@dataclass
class WorkingNodeState:
    proxy: ProxyEnum = field(default=ProxyEnum.SOCK5)
    host: str = field(default='127.0.0.1')
    port: int = field(default=None)
    create_timestamp: int = field(default_factory=timestamp)
    test_timestamp: int = field(default=None)
    pid: int = field(default=None)
    latency: int = field(default=None)
    speed: int = field(default=None)
    using_exports: set[str] = field(default_factory=set)


@dataclass
class AirportSettings:
    id: str
    name: str
    url: str
    exclude_regex: str = field(default=None)


@dataclass
class AirportState:
    subscribe_text: str = None
    nodes: list[WorkingNodeSettings] = field(default_factory=list)
    proxy: ProxyEnum = field(default=None)
    create_timestamp: int = field(default_factory=timestamp)
    pull_timestamp: int = field(default=None)
    success_timestamp: int = field(default=None)

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
    security: str = field(default=None)
    usage: str = field(default=None)
    key_file: str = field(default=None)
    certificate_file: str = field(default=None)
    flow: str = field(default=None)
    select_count: int = field(default=3)
    include_airport_name_regex: str = field(default=None)
    include_working_name_regex: str = field(default=None)
    exclude_airport_name_regex: str = field(default=None)
    exclude_working_name_regex: str = field(default=None)
    account_list: list[list[str]] = field(default=None)


@dataclass
class ExportState:
    executable: Executable = field(default=None)
    pid: int = field(default=None)
    create_timestamp: int = field(default_factory=timestamp)
    select_timestamp: int = field(default=None)


__all__ = [
    'generate_hash',
    'timestamp',
    'WrapEnum',
    'ExecutableEnum',
    'Executable',
    'ProxyEnum',
    'StreamEnum',
    'ObfuscatingEnum',
    'ActionEnum',
    'WorkingNodeSettings',
    'AirportSettings',
    'ExportSettings',
    'WorkingNodeState',
    'AirportState',
    'ExportState',
    'CustomNodeSettings',
    'BaseNodeSettings',
]

import json
import asyncio
import logging
import collections
from exhibition.base import *
from exhibition.message import *
from exhibition.mixin import *
from exhibition.process import *
from exhibition.node.working import WorkingNode


class ExportNode(QueueMixin, StorageMixin, PortPoolMixin):
    LOCKER = asyncio.Lock()

    def __init__(self, settings: ExportSettings) -> None:
        super().__init__()
        self.settings = settings
        self.proc: Process = None
        self.nodes: dict[str, WorkingNode] = dict()
        self.executables: list[Executable] = list()
        self.ordered_nodes: dict[str, list[WorkingNode]] = dict()
        self.best_nodes: list[WorkingNode] = list()

    def __str__(self) -> str:
        return f'<ExportNode {self.settings.id} name:{self.settings.name} >'

    def __repr__(self) -> str:
        return self.__str__()

    def to_dict(self):
        settings = self.settings
        return {
            'id': settings.id,
            'name': settings.name,
            'proxy': settings.proxy.name,
            'host': settings.host,
            'port': settings.port,
            'obfuscating': settings.obfuscating.name if settings.obfuscating else None,
            'uuid': settings.uuid,
            'alterId': settings.alter_id,
            'path': settings.path,
        }

    @property
    def is_using_outdated(self):
        for node in self.best_nodes:
            if node.is_outdated:
                return True
        return False

    @property
    def is_using_dead(self):
        for node in self.best_nodes:
            if not node.is_alive:
                return True
        return False

    def sort_nodes(self):
        airports = collections.defaultdict(list)
        for node in self.nodes.copy().values():
            if not node.airport_id:
                continue
            if not node.is_alive:
                continue
            if node.is_outdated:
                continue
            airport_id = node.airport_id
            airports[airport_id].append(node)
        for nodes in airports.values():
            nodes.sort(key=lambda i: i.speed or -1, reverse=True)
        self.ordered_nodes = airports

    def choose_nodes(self):
        nodes = list()
        for airport_nodes in self.ordered_nodes.copy().values():
            for node in airport_nodes[:3]:
                if not node.speed:
                    continue
                nodes.append(node)
        self.best_nodes = nodes

    def remount_reference(self):
        export_id = self.settings.id
        for node in self.nodes.values():
            if export_id in node.using_exports:
                node.using_exports.remove(export_id)

        for node in self.best_nodes:
            node.using_exports.add(export_id)

    async def apply_nodes(self):
        nodes = self.best_nodes
        logging.debug(f'{self}准备应用最佳节点:{nodes}')
        if self.proc:
            await self.proc.stop()
            self.proc = None
            logging.debug(f'外露节点{self}已经关闭相关进程')
        if not nodes:
            return
        match self.settings.proxy:
            case ProxyEnum.VMESS:
                executable = self.settings.proxy.query_one(self.executables)
                if not executable:
                    return
                match executable.type:
                    case ExecutableEnum.V2RAY:
                        settings = self.settings
                        assert settings.uuid
                        if not settings.obfuscating:
                            inbound = {
                                'listen': settings.host,
                                'port': settings.port,
                                'protocol': 'vmess',
                                'tag': settings.id,
                                'settings': {
                                    'clients': [
                                        {
                                            'alterId': settings.alter_id,
                                            'email': settings.id,
                                            'id': settings.uuid,
                                            'level': 0
                                        }
                                    ],
                                    'default': {
                                        'alterId': settings.alter_id,
                                        'level': 0
                                    },
                                },
                            }
                        else:
                            match settings.obfuscating:
                                case ObfuscatingEnum.WEBSOCKET:
                                    assert settings.path
                                    inbound = {
                                        'listen': settings.host,
                                        'port': settings.port,
                                        'protocol': 'vmess',
                                        'tag': settings.id,
                                        'settings': {
                                            'clients': [
                                                {
                                                    'alterId': settings.alter_id,
                                                    'email': settings.id,
                                                    'id': settings.uuid,
                                                    'level': 0,
                                                },
                                            ],
                                        },
                                        'streamSettings': {
                                            'network': 'ws',
                                            'wsSettings': {
                                                'path': settings.path,
                                            },
                                        },
                                    }
                                case _:
                                    raise ValueError(f'不支持{executable.type}产生{settings.obfuscating}类型的混淆')
                    case _:
                        raise ValueError(f'不支持{executable.type}作为外露服务')
                v2ray_config = {
                    "inbounds": [
                        inbound,
                    ],
                    "outbounds": [
                        {
                            'tag': node.settings.id,
                            'protocol': 'socks',
                            'settings': {
                                'servers': [
                                    {
                                        'address': '127.0.0.1',
                                        'port': node.port,
                                    },
                                ],
                            },
                        } for node in nodes],
                }
                filename = f'EP{self.settings.id}.conf'
                config_path = self.get_path(filename)
                await self.write_file(filename, json.dumps(v2ray_config, indent=2))
                proc = Process(self.settings.id, queue=self.queue)
                await proc.start(executable.path, '-c', config_path)
                self.proc = proc
                logging.debug(f'外露节点{self}已经启动相关进程{proc}')

    def _should_restart(self, force_restart=True):
        if force_restart:
            return True
        if self.is_using_outdated:
            return True
        if self.is_using_dead:
            return True
        if not self.best_nodes:
            return True
        return False

    async def select_nodes(self, force_restart=True):
        if not self._should_restart(force_restart=force_restart):
            return
        self.sort_nodes()
        self.choose_nodes()
        self.remount_reference()
        await self.apply_nodes()
        logging.debug(f'{self}使用节点:{self.best_nodes},当前管理进程:{self.proc}')

    async def on_start(self):
        self.action_timer(ActionEnum.EXPORT_BOOT, 20.0)

    async def on_message(self, message: Message):
        match message.action:
            case ActionEnum.EXPORT_BOOT:
                self.action_timer(ActionEnum.EXPORT_REFRESH, 8 * 60 * 60)
            case ActionEnum.EXPORT_REFRESH:
                self.action_timer(ActionEnum.EXPORT_REFRESH, 8 * 60 * 60)

        match message.action:
            case ActionEnum.STORE_UPDATED:
                nodes = message.nodes
                executables = message.executables
                self.nodes = nodes
                self.executables = executables

        match message.action:
            case ActionEnum.EXPORT_BOOT | ActionEnum.EXPORT_REFRESH:
                self.create_task(self.select_nodes())
            case ActionEnum.STORE_UPDATED:
                self.create_task(self.select_nodes(force_restart=False))


__all__ = [
    'ExportNode',
]

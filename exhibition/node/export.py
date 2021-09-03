import re
import asyncio
import logging
import collections
from exhibition.base import *
from exhibition.message import *
from exhibition.mixin import *
from exhibition.process import *
from exhibition.node.working import WorkingNode
from exhibition.node.airport import AirportNode
from exhibition.selector import *
from exhibition.settings import *


class ExportNode(QueueMixin, StorageMixin, PortPoolMixin):
    LOCKER = asyncio.Lock()

    def __init__(self, settings: ExportSettings, config_settings) -> None:
        super().__init__()
        self.state = ExportState()
        self.settings = settings
        self.config_settings = config_settings
        self.proc: Process = None
        self.nodes: dict[str, WorkingNode] = dict()
        self.executables: list[Executable] = list()
        self.airports: dict[str, AirportNode] = dict()
        self.ordered_nodes: dict[str, list[WorkingNode]] = dict()
        self.best_nodes: list[WorkingNode] = list()

    def __str__(self) -> str:
        return f'<ExportNode {self.settings.id} name:{self.settings.name} >'

    def __repr__(self) -> str:
        return self.__str__()

    def to_dict(self):
        state = self.state
        settings = self.settings
        return {
            'settings': {
                'id': settings.id,
                'name': settings.name,
                'proxy': settings.proxy.name,
                'host': settings.host,
                'port': settings.port,
                'obfuscating': settings.obfuscating.name if settings.obfuscating else None,
                'uuid': settings.uuid,
                'alterId': settings.alter_id,
                'path': settings.path,
            },
            'state': {
                'executable': state.executable.path if state.executable else None,
                'pid': state.pid,
                'createTimestamp': state.create_timestamp,
                'selectTimestamp': state.select_timestamp,
                'usingCount': len(self.best_nodes),
            },
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
            if not node.settings.airport_id:
                continue
            if not node.is_alive:
                continue
            if node.is_outdated:
                continue
            airport_id = node.settings.airport_id
            airports[airport_id].append(node)
        for nodes in airports.values():
            nodes.sort(key=lambda i: i.state.speed or -1, reverse=True)
        self.ordered_nodes = airports

    def choose_nodes(self):
        settings = self.settings
        nodes = list()
        for airport_id, airport_nodes in self.ordered_nodes.copy().items():
            airport = self.airports.get(airport_id)
            if not airport:
                continue
            text = airport.settings.name
            if pattern := settings.include_airport_name_regex:
                if not re.search(pattern, text):
                    logging.info(f'{self}根据包含机场名正则过滤: {text}')
                    continue
            if pattern := settings.exclude_airport_name_regex:
                if re.search(pattern, text):
                    logging.info(f'{self}根据排除机场名正则过滤: {text}')
                    continue
            remain_count = settings.select_count
            for node in airport_nodes:
                if remain_count < 1:
                    break
                text = node.settings.name
                if pattern := settings.include_working_name_regex:
                    if not re.search(pattern, text):
                        logging.info(f'{self}根据包含工作节点名正则过滤: {text}')
                        continue
                if pattern := settings.exclude_working_name_regex:
                    if re.search(pattern, text):
                        logging.info(f'{self}根据排除工作节点名正则过滤: {text}')
                        continue
                if not node.state.speed:
                    continue
                nodes.append(node)
                remain_count -= 1
        self.best_nodes = nodes

    def remount_reference(self):
        export_id = self.settings.id
        for node in self.nodes.values():
            if export_id in node.state.using_exports:
                node.state.using_exports.remove(export_id)

        for node in self.best_nodes:
            state = node.state
            state.using_exports.add(export_id)

    async def apply_nodes(self):
        self.state.select_timestamp = timestamp()
        nodes = self.best_nodes
        logging.info(f'{self}准备应用最佳节点:{nodes}')
        if self.proc:
            await self.proc.stop()
            self.proc = None
            self.state.pid = None
            logging.info(f'外露节点{self}已经关闭相关进程')
        if not nodes:
            logging.info(f'没有最佳节点, 不启动进程')
            return
        selector = Selector.export_node(self.executables, self.settings)
        if not selector:
            self.state.executable = None
            logging.warning(f'外露服务{self}使用的协议{self.settings.proxy}无法匹配所有可执行程序, 不启动进程')
            return
        self.state.executable = selector.executable
        config = selector.export_config(self.settings, [(node.state, node.settings, ) for node in nodes])
        filename = selector.config_filename(f'{self.settings.id}')
        config_path = self.get_path(filename)
        await self.write_file(filename, config)
        proc = Process(self.settings.id, queue=self.queue)
        await proc.start(*selector.process_args(config_path))
        self.proc = proc
        logging.info(f'外露节点{self}已经启动相关进程{proc}')
        self.state.pid = proc.pid

    def _should_restart(self, force_restart=True):
        if force_restart:
            return True
        if self.is_using_outdated:
            return True
        if self.is_using_dead:
            return True
        if not self.best_nodes:
            return True
        if self.state.executable not in self.executables:
            return True
        for node in self.best_nodes:
            state = node.state
            if state.latency is None:
                return True
        return False

    async def select_nodes(self, force_restart=True):
        if not self._should_restart(force_restart=force_restart):
            return
        self.sort_nodes()
        self.choose_nodes()
        self.remount_reference()
        await self.apply_nodes()
        logging.info(f'{self}使用节点:{self.best_nodes},当前管理进程:{self.proc}')

    async def on_start(self):
        self.action_timer(ActionEnum.EXPORT_BOOT, 20.0)

    async def on_message(self, message: Message):
        match message.action:
            case ActionEnum.EXPORT_BOOT:
                config_settings: Settings = self.config_settings()
                self.action_timer(ActionEnum.EXPORT_REFRESH, config_settings.export_reboot_period)
            case ActionEnum.EXPORT_REFRESH if message.from_timer:
                config_settings: Settings = self.config_settings()
                self.action_timer(ActionEnum.EXPORT_REFRESH, config_settings.export_reboot_period)

        match message.action:
            case ActionEnum.STORE_UPDATED:
                nodes = message.nodes
                executables = message.executables
                airports = message.airports
                self.nodes = nodes
                self.executables = executables
                self.airports = airports
            case ActionEnum.PROCESS_EOF:
                self.state.pid = None

        match message.action:
            case ActionEnum.EXPORT_BOOT | ActionEnum.EXPORT_REFRESH:
                self.create_task(self.select_nodes())
            case ActionEnum.STORE_UPDATED:
                self.create_task(self.select_nodes(force_restart=False))


__all__ = [
    'ExportNode',
]

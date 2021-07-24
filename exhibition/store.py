import logging
import os
import toml
import addict
from exhibition.base import *
from exhibition.message import *
from exhibition.node import *
from exhibition.mixin import *
        

class Store(QueueMixin, StorageMixin):
    CONFIG_FILE = 'config.toml'

    def __init__(self) -> None:
        super().__init__()
        self.config: addict.Addict = addict.Addict(dict())
        self.executables: list[Executable] = list()
        self.exports: list[ExportSettings] = list()
        self.nodes: dict[str, WorkingNode] = dict()
        self.airport_nodes: dict[str, AirportNode] = dict()
        self.export_nodes: list[ExportNode] = list()
        self.executable_node: ExecutableNode = None
        self.load_config()
        self._last_saved_body = ''

    def __str__(self) -> str:
        return f'<Store {id(self)} >'

    def __repr__(self) -> str:
        return self.__str__()
    
    def load_config(self):
        config_path = self.get_path(Store.CONFIG_FILE)
        if os.path.exists(config_path):
            config_dict = toml.load(config_path)
            self.config = addict.Addict(config_dict)
        else:
            self.config = addict.Addict(dict())

    async def save_config(self):
        config_path = self.get_path(Store.CONFIG_FILE)
        new_config = self.config.copy()
        new_config.executable = [i.path for i in self.executables]
        new_config.airport = [
            {
                'id': i.settings.id,
                'name': i.settings.name,
                'url': i.settings.url,
            } for i in self.airport_nodes.values()]
        config_body = toml.dumps(new_config)
        if config_body == self._last_saved_body:
            return
        await self.write_file(config_path, config_body)
        self._last_saved_body = config_body
        self.config = addict.Addict(new_config)
        logging.info(f'已成功保存设置')

    @property
    def executable_paths(self) -> list[str]:
        result = list(self.config.executable)
        result = list(set([i for i in result if i and i.strip()]))
        result.sort()
        return result

    @property
    def export_settings(self) -> list[ExportSettings]:
        result = list()
        for item in self.config.export:
            export = ExportSettings(
                id=item.id,
                name=item.name,
                proxy=ProxyEnum[item.proxy] if item.proxy else None,
                host=item.host,
                port=item.port,
                obfuscating=ObfuscatingEnum[item.obfuscating] if item.obfuscating else None,
                path=item.path or None,
                alter_id=item.alterId if isinstance(item.alterId, int) else None,
                uuid=item.uuid or None,
            )
            result.append(export)
        return result

    @property
    def airport_settings(self) -> list[AirportSettings]:
        result = list()
        for item in self.config.airport:
            export = AirportSettings(
                id=item.id,
                name=item.name,
                url=item.url,
            )
            result.append(export)
        return result

    async def broadcast_to_exports(self):
        for node in self.export_nodes:
            if not node.is_alive:
                continue
            message = Message(action=ActionEnum.STORE_UPDATED, nodes=self.nodes, executables=self.executables)
            await node.queue.put(message)

    async def start_nodes(self):
        nodes = self.nodes.copy()
        for node in nodes.values():
            if not node.is_startable:
                continue
            executable = node.settings.proxy.query_one(self.executables)
            if not executable:
                continue
            node.executable = executable
            await node.spawn()
            logging.info(f'启动工作节点{node}')

    async def stop_nodes(self):
        nodes = self.nodes.copy()
        for node_id, node in nodes.items():
            if not node.is_stoppable:
                continue
            await node.stop()
            logging.info(f'停止工作节点{node}')
            if node_id in self.nodes:
                self.nodes.pop(node_id)
                logging.info(f'移除工作节点{node}')

    def mark_node_outdated(self, airport: AirportNode = None):
        for node in self.nodes.values():
            if node.is_outdated:
                continue
            airport_id = node.settings.airport_id
            if airport_id and airport_id not in self.airport_nodes:
                node.is_outdated = True
                logging.info(f'工作节点{node}对应机场不存在, 标记为过时')
            if node.using_exports:
                continue
            if airport:
                if airport_id != airport.settings.id:
                    continue
                for settings in airport.nodes:
                    if node.settings.id == settings.id:
                        break
                else:
                    node.is_outdated = True
                    logging.info(f'工作节点{node}标记为过时')

    def add_nodes(self, airport: AirportNode):
        nodes = self.nodes.copy()
        for settings in airport.nodes:
            if settings.id in self.nodes:
                continue
            node = WorkingNode(settings=settings, store_queue=self.queue)
            node.airport_id = airport.settings.id
            nodes[settings.id] = node
            logging.info(f'添加工作节点{node}')
        self.nodes = nodes
            
    async def on_start(self):
        PortPoolMixin.fill_port_pool(9000, 9999)
        self.executable_node = ExecutableNode(paths=self.executable_paths, store_queue=self.queue)
        await self.executable_node.spawn(on_start_async=False)
        for settings in self.airport_settings:
            airport_node = AirportNode(settings=settings, store_quque=self.queue)
            message = Message(action=ActionEnum.AIRPORT_UPDATED, airport=airport_node)
            await self.queue.put(message)
        for settings in self.export_settings:
            node = ExportNode(settings=settings)
            await node.spawn()
            self.export_nodes.append(node)
        self.action_timer(ActionEnum.STORE_STOP_NODES, 15)
        self.action_timer(ActionEnum.STORE_START_NODES, 8)

    async def stop(self):
        await super().stop()
        if self.executable_node:
            await self.executable_node.stop()
            self.executable_node = None
        for node in self.airport_nodes.values():
            if node.is_alive:
                await node.stop()
        self.airport_nodes.clear()
        for node in self.export_nodes:
            await node.stop()
        self.export_nodes = list()
        for node in self.nodes.values():
            if node.is_alive:
                await node.stop()
        self.nodes.clear()

    async def on_message(self, message: Message):
        match message.action:
            case ActionEnum.STORE_STOP_NODES:
                self.action_timer(ActionEnum.STORE_STOP_NODES, 15)
            case ActionEnum.STORE_START_NODES:
                self.action_timer(ActionEnum.STORE_START_NODES, 300)
        
        match message.action:
            case ActionEnum.EXECUTABLE_UPDATED:
                node = self.executable_node
                self.executables = node.executables.copy()
                await self.save_config()
            case ActionEnum.AIRPORT_UPDATED:
                airport: AirportNode = message.airport
                airport_id = airport.settings.id
                if airport_id not in self.airport_nodes:
                    await airport.spawn()
                    new_nodes = self.airport_nodes.copy()
                    new_nodes[airport_id] = airport
                    self.airport_nodes = new_nodes
                self.mark_node_outdated(airport=airport)
                self.add_nodes(airport)
            case ActionEnum.AIRPORT_REMOVE:
                airport: AirportNode = message.airport
                airport_id = airport.settings.id
                if airport.is_alive:
                    await airport.stop()
                if airport_id in self.airport_nodes:
                    self.airport_nodes = {k: v for k, v in self.airport_nodes.items() if k != airport_id}
                self.mark_node_outdated(airport=airport)
            case ActionEnum.STORE_STOP_NODES:
                self.mark_node_outdated()
                self.create_task(self.stop_nodes())
            case ActionEnum.STORE_START_NODES:
                self.create_task(self.start_nodes())
        
        match message.action:
            case ActionEnum.EXECUTABLE_UPDATED | ActionEnum.AIRPORT_UPDATED:
                await self.broadcast_to_exports()

        match message.action:
            case ActionEnum.EXECUTABLE_UPDATED | ActionEnum.AIRPORT_UPDATED | ActionEnum.AIRPORT_REMOVE:
                await self.save_config()


__all__ = [
    'Store',
]

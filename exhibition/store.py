import logging
import os
import toml
import addict
from exhibition.base import *
from exhibition.message import *
from exhibition.node import *
from exhibition.mixin import *
from exhibition.selector import *
from exhibition.settings import *
        

class Store(QueueMixin, StorageMixin):
    CONFIG_FILE = 'config.toml'

    def __init__(self) -> None:
        super().__init__()
        self.config: addict.Addict = addict.Addict(dict())
        self.executables: list[Executable] = list()
        self.custom_nodes: list[CustomNodeSettings] = list()
        self.working_nodes: dict[str, WorkingNode] = dict()
        self.airport_nodes: dict[str, AirportNode] = dict()
        self.export_nodes: list[ExportNode] = list()
        self.executable_node: ExecutableNode = None
        self.settings: Settings = None
        self._last_saved_body = ''
        self.load_config()

    def __str__(self) -> str:
        return f'<Store>'

    def __repr__(self) -> str:
        return self.__str__()
    
    def load_config(self):
        config_path = self.get_path(Store.CONFIG_FILE)
        if os.path.exists(config_path):
            config_dict = toml.load(config_path)
            self.config = addict.Addict(config_dict)
        else:
            self.config = addict.Addict(dict())
        self.settings = Settings(self.config)

    async def save_config(self):
        config_path = self.get_path(Store.CONFIG_FILE)
        new_config = self.config.copy()
        new_config.executable = [i.path for i in self.executables]
        new_config.airport = [
            {
                'id': i.settings.id,
                'name': i.settings.name,
                'url': i.settings.url,
                'excludeRegex': i.settings.exclude_regex,
            } for i in self.airport_nodes.values()]
        new_config.export = [
            {
                'id': i.settings.id,
                'name': i.settings.name,
                'proxy': i.settings.proxy.name,
                'host': i.settings.host,
                'port': i.settings.port,
                'obfuscating': i.settings.obfuscating.name if i.settings.obfuscating else None,
                'path': i.settings.path,
                'alterId': i.settings.alter_id,
                'uuid': i.settings.uuid,
                'security': i.settings.security,
                'usage': i.settings.usage,
                'keyFile': i.settings.key_file,
                'certificateFile': i.settings.certificate_file,
                'selectCount': i.settings.select_count,
                'includeAirportNameRegex': i.settings.include_airport_name_regex,
                'includeWorkingNameRegex': i.settings.include_working_name_regex,
                'excludeAirportNameRegex': i.settings.exclude_airport_name_regex,
                'excludeWorkingNameRegex': i.settings.exclude_working_name_regex,
                'accountList': i.settings.account_list,
            } for i in self.export_nodes]
        new_config.custom = [i.to_dict() for i in self.custom_nodes]
        new_config.settings = self.settings.to_dict()
        config_body = toml.dumps(new_config)
        if config_body == self._last_saved_body:
            return
        await self.write_file(config_path, config_body)
        self._last_saved_body = config_body
        self.config = addict.Addict(new_config)
        logging.info(f'已成功保存设置')
        self.settings = Settings(self.config)

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
            item: addict.Addict = item
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
                security=item.security or None,
                usage=item.usage or None,
                key_file=item.keyFile or None,
                certificate_file=item.certificateFile or None,
                select_count=item.selectCount,
                include_airport_name_regex=item.includeAirportNameRegex,
                include_working_name_regex=item.includeWorkingNameRegex,
                exclude_airport_name_regex=item.excludeAirportNameRegex,
                exclude_working_name_regex=item.excludeWorkingNameRegex,
                account_list=item.accountList or None,
            )
            result.append(export)
        return result

    @property
    def custom_node_settings(self) -> list[CustomNodeSettings]:
        result = list()
        for item in self.config.custom:
            item: addict.Addict = item
            export = CustomNodeSettings(
                id=item.id,
                name=item.name,
                proxy=ProxyEnum[item.proxy] if item.proxy else None,
                host=item.host,
                port=item.port,
                obfuscating=ObfuscatingEnum[item.obfuscating] if item.obfuscating else None,
                path=item.path or None,
                alter_id=item.alterId if isinstance(item.alterId, int) else None,
                uuid=item.uuid or None,
                security=item.security,
                encryption=item.encryption,
                flow=item.flow,
                encrypt_method=item.encryptMethod,
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
                exclude_regex=item.excludeRegex or None,
            )
            result.append(export)
        return result

    async def broadcast_to_exports(self):
        for node in self.export_nodes:
            if not node.is_alive:
                continue
            message = Message(
                action=ActionEnum.STORE_UPDATED,
                nodes=self.working_nodes,
                executables=self.executables,
                airports=self.airport_nodes,
            )
            node | message

    async def start_nodes(self):
        nodes = self.working_nodes.copy()
        for node in nodes.values():
            if not node.is_startable:
                continue
            selector = Selector.working_node(self.executables, node.settings)
            if not selector:
                logging.warning(f'工作节点{node}使用的协议无法匹配所有可执行程序')
                continue
            node.selector = selector
            await node.spawn()
            logging.info(f'启动工作节点{node}')

    async def stop_nodes(self):
        nodes = self.working_nodes.copy()
        for node_id, node in nodes.items():
            if not node.is_stoppable:
                continue
            await node.stop()
            logging.info(f'停止工作节点{node}')
            if node_id in self.working_nodes:
                self.working_nodes.pop(node_id)
                logging.info(f'移除工作节点{node}')

    def mark_node_outdated(self, airport: AirportNode = None):
        for node in self.working_nodes.values():
            if node.is_outdated:
                continue
            airport_id = node.settings.airport_id
            if airport_id and airport_id not in self.airport_nodes:
                node.is_outdated = True
                logging.info(f'工作节点{node}对应机场不存在, 标记为过时')
            if not airport_id:
                for settings in self.custom_nodes:
                    if node.settings.id == settings.id:
                        break
                else:
                    node.is_outdated = True
                    logging.info(f'工作节点{node}对自定义节点配置不存在, 标记为过时')
            if node.state.using_exports:
                continue
            if airport:
                if airport_id != airport.settings.id:
                    continue
                for settings in airport.state.nodes:
                    if node.settings.id == settings.id:
                        break
                else:
                    node.is_outdated = True
                    logging.info(f'工作节点{node}不在机场节点中, 标记为过时')

    def add_nodes(self, airport: AirportNode):
        nodes = self.working_nodes.copy()
        for settings in airport.state.nodes:
            if settings.id in self.working_nodes:
                continue
            node = WorkingNode(settings=settings, config_settings=lambda : self.settings)
            nodes[settings.id] = node
            logging.info(f'添加工作节点{node}')
        self.working_nodes = nodes

    def add_custom_node(self, settings: CustomNodeSettings):
        if settings in self.custom_nodes:
            return
        nodes = self.custom_nodes.copy()
        nodes.append(settings)
        self.custom_nodes = nodes
        if settings.id in self.working_nodes:
            return
        working_settings = WorkingNodeSettings.from_custom_node(settings)
        nodes = self.working_nodes.copy()
        node = WorkingNode(settings=working_settings, config_settings=lambda : self.settings)
        nodes[settings.id] = node
        self.working_nodes = nodes
            
    async def on_start(self):
        PortPoolMixin.fill_port_pool(*self.settings.working_port_range)
        self.executable_node = ExecutableNode(paths=self.executable_paths, store=self)
        self.custom_nodes = self.custom_node_settings
        await self.executable_node.spawn(on_start_async=False)
        for settings in self.custom_nodes:
            self.add_custom_node(settings)
        for settings in self.airport_settings:
            airport_node = AirportNode(settings=settings, store=self)
            message = Message(action=ActionEnum.AIRPORT_UPDATED, airport=airport_node)
            self | message
        for settings in self.export_settings:
            node = ExportNode(settings=settings, config_settings=lambda : self.settings)
            await node.spawn()
            self.export_nodes.append(node)
        self.action_timer(ActionEnum.STORE_STOP_NODES, 15)
        self.action_timer(ActionEnum.STORE_START_NODES, 20)

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
        for node in self.working_nodes.values():
            if node.is_alive:
                await node.stop()
        self.working_nodes.clear()

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
                self | Message(action=ActionEnum.STORE_START_NODES)
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
            case ActionEnum.EXPORT_UPDATE:
                export: ExportNode = message.export
                await export.spawn()
                export_nodes = self.export_nodes.copy()
                export_nodes.append(export)
                self.export_nodes = export_nodes
            case ActionEnum.EXPORT_REMOVE:
                export: ExportNode = message.export
                if export.is_alive:
                    await export.stop()
                export_nodes = [i for i in self.export_nodes if i != export]
                self.export_nodes = export_nodes
            case ActionEnum.CUSTOM_NODE_UPDATED:
                settings = message.custom
                self.add_custom_node(settings)
            case ActionEnum.CUSTOM_NODE_REMOVE:
                node = message.custom
                self.custom_nodes.remove(node)
                self.mark_node_outdated()
        
        match message.action:
            case ActionEnum.EXECUTABLE_UPDATED | ActionEnum.AIRPORT_UPDATED | ActionEnum.AIRPORT_REMOVE | \
                ActionEnum.EXPORT_UPDATE | ActionEnum.EXPORT_REMOVE:
                await self.broadcast_to_exports()

        match message.action:
            case ActionEnum.EXECUTABLE_UPDATED | ActionEnum.AIRPORT_UPDATED | ActionEnum.AIRPORT_REMOVE | \
                ActionEnum.EXPORT_UPDATE | ActionEnum.EXPORT_REMOVE | \
                ActionEnum.CUSTOM_NODE_UPDATED | ActionEnum.CUSTOM_NODE_REMOVE | ActionEnum.STORE_SAVE_SETTINGS:
                await self.save_config()


__all__ = [
    'Store',
]

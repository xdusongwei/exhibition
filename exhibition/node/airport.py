import asyncio
import logging
from exhibition.base import *
from exhibition.message import *
from exhibition.mixin import *


class AirportNode(QueueMixin, SubscribeMixin, HttpMixin):
    def __init__(self, settings: AirportSettings, store_quque: asyncio.Queue) -> None:
        super().__init__()
        self.settings = settings
        self.store_queue = store_quque
        self.subscribe_text = None
        self.nodes: list[NodeSettings] = list()
        self.proxy: ProxyEnum = None

    def __str__(self) -> str:
        return f'<AirportNode {self.settings.id} name:{self.settings.name} >'

    def __repr__(self) -> str:
        return self.__str__()

    @property
    def node_count(self):
        return len(self.nodes)

    def to_dict(self):
        settings = self.settings
        return {
            'id': settings.id,
            'name': settings.name,
            'url': settings.url,
            'proxy': self.proxy.name if self.proxy else None,
            'nodeCount': self.node_count,
        }

    async def update_settings(self):
        settings_list = None
        url = self.settings.url
        text = await self.download_text(url)
        if not text:
            logging.warning(f'{url}下载内容为空')
            return
        proxy = self.detect_subscribe_type(text)
        self.proxy = proxy
        match proxy:
            case ProxyEnum.VMESS:
                settings_list = self.decode_vmess_nodes(text)
            case ProxyEnum.SHADOWSOCKS:
                settings_list = self.decode_shadowsocks_nodes(text)
            case _:
                logging.error(f'{url} 无法判断内容的代理协议')
        if settings_list:
            for settings in settings_list:
                settings.airport_id = self.settings.id
        if settings_list:
            self.nodes = settings_list
        await self.store_queue.put(Message(action=ActionEnum.AIRPORT_UPDATED, airport=self))

    async def on_start(self):
        message = Message(action=ActionEnum.AIRPORT_SUBSCRIBE)
        await self.queue.put(message)

    async def on_message(self, message: Message):
        match message.action:
            case ActionEnum.AIRPORT_SUBSCRIBE:
                self.action_timer(ActionEnum.AIRPORT_SUBSCRIBE, 1800.0)

        match message.action:
            case ActionEnum.AIRPORT_SUBSCRIBE:
                self.create_task(self.update_settings())


__all__ = [
    'AirportNode',
]

import re
import logging
from exhibition.base import *
from exhibition.message import *
from exhibition.mixin import *


class AirportNode(QueueMixin, SubscribeMixin, HttpMixin):
    def __init__(self, settings: AirportSettings, store: QueueMixin) -> None:
        super().__init__()
        self.state: AirportState = AirportState()
        self.settings = settings
        self.store = store

    def __str__(self) -> str:
        return f'<AirportNode {self.settings.id} name:{self.settings.name} >'

    def __repr__(self) -> str:
        return self.__str__()

    @property
    def node_count(self):
        return len(self.state.nodes)

    def to_dict(self):
        state = self.state
        settings = self.settings
        return {
            'settings': {
                'id': settings.id,
                'name': settings.name,
                'url': settings.url,
                'excludeRegex': settings.exclude_regex,
            },
            'state': {
                'proxy': state.proxy.name if state.proxy else None,
                'createTimestamp': state.create_timestamp,
                'pullTimestamp': state.pull_timestamp,
                'successTimestamp': state.success_timestamp,
                'nodeCount': self.node_count,
            },
        }

    async def update_settings(self):
        self.state.pull_timestamp = timestamp()
        settings_list = None
        url = self.settings.url
        text = self.state.subscribe_text = await self.download_text(url)
        if not text:
            logging.warning(f'{url}下载内容为空')
            return
        proxy = self.detect_subscribe_type(text)
        self.state.proxy = proxy
        match proxy:
            case ProxyEnum.VMESS:
                settings_list = self.decode_vmess_nodes(text)
            case ProxyEnum.SHADOWSOCKS:
                settings_list = self.decode_shadowsocks_nodes(text)
            case _:
                logging.error(f'{url} 无法判断内容的代理协议')
        if settings_list:
            for settings in settings_list.copy():
                settings.airport_id = self.settings.id
                if regex := self.settings.exclude_regex:
                    if re.search(regex, settings.name):
                        logging.info(f'根据正则表达式排除机场节点:{settings}')
                        settings_list.remove(settings)
        if settings_list:
            self.state.nodes = settings_list
        self.store | Message(action=ActionEnum.AIRPORT_UPDATED, airport=self)
        self.state.success_timestamp = timestamp()

    async def on_start(self):
        message = Message(action=ActionEnum.AIRPORT_SUBSCRIBE, from_timer=True)
        self | message

    async def on_message(self, message: Message):
        match message.action:
            case ActionEnum.AIRPORT_SUBSCRIBE if message.from_timer:
                self.action_timer(ActionEnum.AIRPORT_SUBSCRIBE, 1800.0)

        match message.action:
            case ActionEnum.AIRPORT_SUBSCRIBE:
                self.create_task(self.update_settings())


__all__ = [
    'AirportNode',
]

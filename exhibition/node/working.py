import json
import time
import random
import asyncio
import logging
from exhibition.base import *
from exhibition.message import *
from exhibition.mixin import *
from exhibition.process import *


class WorkingNode(QueueMixin, HttpMixin, StorageMixin, PortPoolMixin):
    TEST_LOCKS = [asyncio.Lock() for _ in range(8)]

    def __init__(self, settings: NodeSettings, store_queue: asyncio.Queue) -> None:
        super().__init__()
        self.executable: Executable = None
        self.settings = settings
        self.store_queue = store_queue
        self.port = None
        self.latency = None
        self.speed = None
        self.proc: Process = None
        self.using_exports = set()
        self.is_outdated = False
        self.is_process_dead = False
        self.airport_id = None

    def __str__(self) -> str:
        return f'<WorkingNode {self.settings.id} outbound:{self.settings.proxy}://{self.settings.host}:{self.settings.port} >'

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
            'uuid': settings.uuid,
            'alterId': settings.alter_id,
            'tls': settings.tls,
            'airportId': settings.airport_id,
            'latency': self.latency,
            'usingCount': len(self.using_exports),
        }

    @property
    def proxy(self) -> ProxyEnum:
        return ProxyEnum.SOCK5

    @property
    def is_startable(self) -> bool:
        if self.is_alive:
            return False
        if self.is_outdated:
            return False
        return True

    @property
    def is_stoppable(self) -> bool:
        if not self.is_alive:
            return False
        if not self.is_outdated:
            return False
        return True

    async def test_node(
            self,
            get_url: str,
            request_timeout: int = 8,
    ):
        lock = random.choice(self.TEST_LOCKS)
        async with lock:
            await self._test_loop(get_url, request_timeout)
            logging.debug(f'{self}延迟结果为{self.latency}')

    async def _test_loop(
            self,
            get_url: str,
            request_timeout,
    ):
        latency = None
        speed = None
        success_times = 0
        total_times = 3
        response_times = 2
        for i in range(total_times):
            try:
                await asyncio.sleep(2)
                begin_time = time.time()
                proxy = f'socks5://127.0.0.1:{self.port}'
                binary = await self.download_binary(get_url, timeout=request_timeout, proxy=proxy)
                length = len(binary or b'')
                success_times += 1
                finish_time = time.time()
                current_latency = int((finish_time - begin_time) * 1000)
                if latency is None or current_latency < latency:
                    latency = current_latency
                current_speed = int(length / (current_latency or 1) * 1000)
                if speed is None or speed > current_speed:
                    speed = current_speed
            except asyncio.CancelledError as e:
                raise e
            except Exception as e:
                if total_times - i - 1 + success_times < response_times:
                    latency = None
                    speed = None
                    break
        self.latency = latency
        self.speed = speed

    async def stop(self):
        await super().stop()
        if self.port:
            self.return_port(self.port)
            self.port = None
        if self.proc:
            await self.proc.stop()
            self.proc = None
        self.speed = None
        self.latency = None

    async def on_start(self):
        port = 0
        try:
            port = self.borrow_port()
            match self.settings.proxy:
                case ProxyEnum.VMESS:
                    v2ray_config = {
                        "inbounds": [
                            {
                                "listen": "127.0.0.1",
                                "port": port,
                                "protocol": "socks",
                                "tag": self.settings.id,
                            },
                        ],
                        "outbounds": [
                            {
                                'tag': 'v2ray',
                                'protocol': 'vmess',
                                'settings': {
                                    'vnext': [
                                        {
                                            "address": self.settings.host,
                                            "port": self.settings.port,
                                            "users": [
                                                {
                                                    "alterId": self.settings.alter_id,
                                                    "id": self.settings.uuid,
                                                },
                                            ],
                                        },
                                    ],
                                },
                            },
                        ],
                    }
                    filename = f'{self.settings.id}.conf'
                    config_path = self.get_path(filename)
                    await self.write_file(filename, json.dumps(v2ray_config, indent=2))
                    proc = Process(self.settings.id, queue=self.queue)
                    await proc.start(self.executable.path, '-c', config_path)
                case ProxyEnum.SHADOWSOCKS:
                    ss_info = self.settings.origin.copy()
                    ss_info['remarks'] = 'remarks'
                    ss_info['local_address'] = '127.0.0.1'
                    ss_info['local_port'] = port
                    filename = f'{self.settings.id}.conf'
                    config_path = self.get_path(filename)
                    await self.write_file(filename, json.dumps(ss_info, indent=2))
                    proc = Process(self.settings.id, queue=self.queue)
                    await proc.start(self.executable.path, '-c', config_path)
            self.proc = proc
            self.port = port
            self.is_process_dead = False
            logging.debug(f'工作节点{self}成功启动进程{self.proc}')
        except Exception as e:
            if port:
                self.return_port(port)
            self.is_process_dead = True
            if self.proc:
                await self.proc.stop()
                self.proc = None
            raise e

    async def on_message(self, message: Message):
        match message.action:
            case ActionEnum.PROCESS_STARTED:
                self_message = Message(ActionEnum.NODE_LATENCY_TEST)
                await self.queue.put(self_message)
            case ActionEnum.PROCESS_TEXT:
                pass
            case ActionEnum.PROCESS_EOF:
                self.is_process_dead = True
                self.proc = None
            case ActionEnum.PROCESS_STOPPED:
                self.is_process_dead = True
            case ActionEnum.NODE_LATENCY_TEST:
                if self.is_alive and not self.is_process_dead:
                    self.create_task(self.test_node('https://ssl.gstatic.com/gb/images/p2_edfc3681.png'))
                    self.action_timer(ActionEnum.NODE_LATENCY_TEST, 1200.0 + random.randrange(0, 300))


__all__ = [
    'WorkingNode',
]

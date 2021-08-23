import random
import asyncio
import logging
from exhibition.base import *
from exhibition.message import *
from exhibition.mixin import *
from exhibition.process import *
from exhibition.selector import *
from exhibition.settings import *


class WorkingNode(QueueMixin, HttpMixin, StorageMixin, PortPoolMixin):
    TEST_LOCKS = [asyncio.Lock() for _ in range(8)]

    def __init__(self, settings: WorkingNodeSettings, config_settings) -> None:
        super().__init__()
        self.selector: ExecutableAbstract = None
        self.state: WorkingNodeState = WorkingNodeState()
        self.settings = settings
        self.config_settings = config_settings
        self.proc: Process = None
        self.is_outdated = False
        self.is_process_dead = False

    def __str__(self) -> str:
        settings = self.settings
        return f'<WorkingNode {settings.id} settings:{settings} >'

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
                'uuid': settings.uuid,
                'alterId': settings.alter_id,
                'tls': settings.tls,
                'airportId': settings.airport_id,
            },
            'state': {
                'latency': state.latency,
                'createTimestamp': state.create_timestamp,
                'testTimestamp': state.test_timestamp,
                'pid': state.pid,
                'usingCount': len(self.state.using_exports),
                'host': state.host,
                'port': state.port,
            },
        }

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
            self.state.test_timestamp = timestamp()
            await self._test_loop(get_url, request_timeout)
            logging.info(f'{self}延迟结果为 {self.state.latency} ms')

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
        assert self.state.proxy == ProxyEnum.SOCKS5
        for i in range(total_times):
            try:
                await asyncio.sleep(2)
                begin_time = timestamp()
                proxy = f'socks5://{self.state.host}:{self.state.port}'
                binary = await self.download_binary(get_url, timeout=request_timeout, proxy=proxy)
                length = len(binary or b'')
                success_times += 1
                finish_time = timestamp()
                current_latency = finish_time - begin_time
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
        self.state.latency = latency
        self.state.speed = speed

    async def stop(self):
        await super().stop()
        if self.state.port:
            self.return_port(self.state.port)
            self.state.port = None
        if self.proc:
            await self.proc.stop()
            self.proc = None
            self.state.pid = None
        self.state.speed = None
        self.state.latency = None

    async def on_start(self):
        port = 0
        try:
            port = self.borrow_port()
            self.state.port = port
            config = self.selector.working_config(self.state, self.settings)
            filename = self.selector.config_filename(f'{self.settings.id}')
            config_path = self.get_path(filename)
            await self.write_file(filename, config)
            proc = Process(self.settings.id, queue=self.queue)
            await proc.start(*self.selector.process_args(config_path=config_path))
            logging.info(f'工作节点{self}成功启动进程{proc}')
            self.proc = proc
            self.state.port = port
            self.is_process_dead = False
            self.state.pid = self.proc.pid
        except Exception as e:
            if port:
                self.return_port(port)
            self.state.port = None
            self.is_process_dead = True
            if self.proc:
                await self.proc.stop()
                self.proc = None
            raise e

    async def on_message(self, message: Message):
        match message.action:
            case ActionEnum.PROCESS_STARTED:
                self_message = Message(ActionEnum.WORKING_LATENCY_TEST)
                self | self_message
            case ActionEnum.PROCESS_TEXT:
                pass
            case ActionEnum.PROCESS_EOF:
                self.is_process_dead = True
                self.proc = None
            case ActionEnum.PROCESS_STOPPED:
                self.is_process_dead = True
            case ActionEnum.WORKING_LATENCY_TEST:
                if self.is_alive and not self.is_process_dead:
                    settings: Settings = self.config_settings()
                    self.create_task(self.test_node(settings.test_url))
                    self.action_timer(ActionEnum.WORKING_LATENCY_TEST, 1800.0 + random.randrange(0, 3600))


__all__ = [
    'WorkingNode',
]

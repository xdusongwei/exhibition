import os
import json
import base64
import asyncio
import logging
import traceback
from pathlib import Path
import yarl
import addict
import aiohttp
import aiofiles
import aiofiles.os
from aiohttp_socks import ProxyConnector
from exhibition.base import *
from exhibition.message import *
from exhibition.timer import *


class TimerMixin:
    __TIMERS: dict[object, dict[object, Timer]] = dict()

    async def stop_timer(self, key):
        if self in self.__TIMERS and key in self.__TIMERS[self] and self.__TIMERS[self][key].task:
            await self.__TIMERS[self][key].stop()
            del self.__TIMERS[self][key]
            if not self.__TIMERS[self]:
                del self.__TIMERS[self]

    async def cancel_timers(self):
        if self not in self.__TIMERS:
            return
        waiting_list = list()
        for timer in self.__TIMERS[self].values():
            if not timer.task:
                timer.clean()
                continue
            waiting_list.append(timer.stop())
        if waiting_list:
            await asyncio.wait(waiting_list)
            waiting_list.clear()
        self.__TIMERS[self].clear()
        del self.__TIMERS[self]

    def set_timer(self, key, timer: Timer):
        if self not in self.__TIMERS:
            self.__TIMERS[self] = dict()
        if key in self.__TIMERS[self]:
            last_timer = self.__TIMERS[self][key]
            if last_timer.task:
                last_timer.task.cancel()
        self.__TIMERS[self][key] = timer
        timer.start()


class QueueMixin(TimerMixin):
    __TASKS: dict[object, set[asyncio.Task]] = dict()

    def __init__(self) -> None:
        super().__init__()
        self.queue = asyncio.Queue()
        self.is_alive = False
        self.task: asyncio.Task = None
        self.on_start_async = True

    def __or__(self, other):
        assert isinstance(other, Message)
        if not self.is_alive:
            return
        async def _task():
            await self.queue.put(other)
        self.create_task(_task())
        return self

    async def _loop(self):
        if self.on_start_async:
            try:
                await self.on_start()
            except Exception as e:
                logging.error(f'{self}启动失败: {e}')
                self.is_alive = False
                self.task = None
                return
        message = None
        while True:
            try:
                message: Message = await self.queue.get()
                logging.debug(f'{self}: {message}')
                if message.action == ActionEnum.NODE_SHUTDOWN:
                    self.is_alive = False
                    self.task = None
                    break
                await self.on_message(message)
            except asyncio.CancelledError as e:
                self.is_alive = False
                self.task = None
                break
            except Exception as e:
                logging.error(f'{self}处理消息{message}失败: {e}')

    async def on_start(self):
        pass

    async def on_message(self, message: Message):
        raise NotImplementedError

    async def spawn(self, on_start_async=True, wait=False):
        if self.is_alive:
            raise ValueError(f'{self}已经运行')
        self.is_alive = True
        self.on_start_async = on_start_async
        if not self.on_start_async:
            try:
                await self.on_start()
            except Exception as e:
                logging.error(f'{self}启动时调用 on_start 失败: {e}')
                self.is_alive = False
                self.task = None
                return
        self.task = asyncio.create_task(self._loop(), name=f'{self}')
        if wait:
            await self.task

    async def stop(self):
        if not self.is_alive:
            raise ValueError(f'{self}未运行')
        if self.task:
            self.task.cancel()
            await self.task
            self.task = None
        await self.cancel_timers()
        await self.cancel_tasks()
        self.is_alive = False

    def create_task(
            self,
            awaitable,
            error_message: Message=None,
            finally_message: Message=None,
            queue: asyncio.Queue=None,
            timeout=None,
    ) -> asyncio.Task:
        queue = queue or self.queue
        async def executor():
            result = None
            try:
                if timeout is None:
                    result = await awaitable
                else:
                    result = await asyncio.wait_for(awaitable, timeout)
                if isinstance(result, Message) and queue:
                    await queue.put(result)
            except Exception as e:
                format_exception = traceback.format_exception(e)
                if error_message:
                    error_message.exception = (e, format_exception, )
                    await self.queue.put(error_message)
                else:
                    logging.error(f'执行{self}的子任务{awaitable}失败: {e},{format_exception}')
            finally:
                task = asyncio.current_task()
                if self in self.__TASKS and task in self.__TASKS[self]:
                    self.__TASKS[self].remove(task)
                    if not self.__TASKS[self]:
                        del self.__TASKS[self]
                if finally_message:
                    await self.queue.put(finally_message)
        task = asyncio.create_task(executor())
        if self not in self.__TASKS:
            self.__TASKS[self] = set()
        self.__TASKS[self].add(task)
        return task

    async def cancel_tasks(self):
        if self not in self.__TASKS:
            return
        waiting_list = list()
        for task in self.__TASKS[self]:
            task.cancel()
            waiting_list.append(task)
        self.__TASKS[self].clear()
        del self.__TASKS[self]
        if waiting_list:
            await asyncio.wait(waiting_list)
            waiting_list.clear()

    def action_timer(self, action: ActionEnum, interval):
        self.set_timer(action, Timer(queue=self.queue, data=action, interval=interval))


class HttpMixin:
    @classmethod
    async def download_binary(cls, url, timeout=12, proxy=None) -> bytes:
        async with aiohttp.ClientSession(**cls._create_session_args(proxy)) as session:
            async with session.get(**cls._create_request_args(url, timeout, proxy)) as resp:
                assert resp.status == 200
                binary = await resp.read()
        return binary

    @classmethod
    async def download_text(cls, url, timeout=12, proxy=None) -> str:
        async with aiohttp.ClientSession(**cls._create_session_args(proxy)) as session:
            async with session.get(**cls._create_request_args(url, timeout, proxy)) as resp:
                assert resp.status == 200
                text = await resp.text()
        return text

    @classmethod
    def _create_session_args(cls, proxy: str):
        if proxy is None:
            return dict()
        if proxy.lower().startswith('socks5://'):
            connector = ProxyConnector.from_url(proxy)
            return dict(
                connector=connector,
            )
        return dict()

    @classmethod
    def _create_request_args(cls, url, timeout, proxy: str):
        if proxy is not None and proxy.lower().startswith('http://'):
            return dict(
                url=url,
                timeout=timeout,
                proxy=proxy,
            )
        if proxy is not None and proxy.lower().startswith('https://'):
            return dict(
                url=url,
                timeout=timeout,
                proxy=proxy,
            )
        return dict(
            url=url,
            timeout=timeout,
            proxy=None,
        )


class SubscribeMixin:
    @classmethod
    def detect_subscribe_type(cls, text) -> None | ProxyEnum:
        if cls._decode_shadowsocks_config(text=text):
            return ProxyEnum.SHADOWSOCKS
        if cls._decode_sip002_format(text=text):
            return ProxyEnum.SHADOWSOCKS
        try:
            base64.urlsafe_b64decode(text + "=" * (-len(text) % 4)).split()
            return ProxyEnum.VMESS
        except Exception:
            pass
        return None

    @classmethod
    def _decode_shadowsocks_config(cls, text: str) -> list[WorkingNodeSettings]:
        try:
            d = json.loads(text)
            d = addict.Dict(d)
            items = d.configs
            proxy = ProxyEnum.SHADOWSOCKS
            result = [WorkingNodeSettings.from_subscribe(proxy, origin) for origin in items]
            return result
        except Exception:
            return list()

    @classmethod
    def _decode_sip002_format(cls, text: str) -> list[WorkingNodeSettings]:
        result = list()
        try:
            items = base64.urlsafe_b64decode(text + "=" * (-len(text) % 4)).split()
            items = [item for item in items if item]
            for item in items:
                url = yarl.URL(item.decode('utf8'))
                if url.scheme != 'ss':
                    break
                user = url.user
                user = base64.urlsafe_b64decode(user + "=" * (-len(user) % 4)).decode('utf8')
                method, password = user.split(':')
                remarks = url.fragment
                plugin_parts = url.query.get('plugin').split(';')
                plugin = plugin_parts[0]
                plugin_opts = ';'.join(plugin_parts[1:])
                origin = {
                    'server': url.host,
                    'server_port': int(url.port),
                    'password': password,
                    'method': method,
                    'remarks': remarks,
                    'plugin': plugin,
                    'plugin_opts': plugin_opts,
                    'timeout': 5,
                }
                proxy = ProxyEnum.SHADOWSOCKS
                settings = WorkingNodeSettings.from_subscribe(proxy, origin)
                result.append(settings)
        except Exception:
            pass
        return result

    @classmethod
    def decode_shadowsocks_nodes(cls, text: str) -> list[WorkingNodeSettings]:
        if nodes := cls._decode_shadowsocks_config(text=text):
            return nodes
        if nodes := cls._decode_sip002_format(text=text):
            return nodes
        return list()

    @classmethod
    def decode_vmess_nodes(cls, text: str) -> list[WorkingNodeSettings]:
        vmess_lines = base64.urlsafe_b64decode(text + "=" * (-len(text) % 4)).split()
        config_list = [json.loads(base64.urlsafe_b64decode(line.replace(b"vmess://", b""))) for line in vmess_lines]
        proxy = ProxyEnum.VMESS
        result = [WorkingNodeSettings.from_subscribe(proxy, origin) for origin in config_list]
        return result


class StorageMixin:
    CONFIG_ROOT = '.exhibition'
    WRITE_LOCK = asyncio.Lock()

    @staticmethod
    def working_path() -> str:
        home_path = str(Path.home())
        working_path = os.path.join(home_path, StorageMixin.CONFIG_ROOT)
        working_path = os.path.expanduser(working_path)
        os.makedirs(working_path, exist_ok=True)
        return working_path

    @classmethod
    async def write_file(cls, name: str, body: str):
        assert name
        assert body
        path = cls.get_path(name)
        async with cls.WRITE_LOCK:
            async with aiofiles.open(path, 'w') as afp:
                await afp.write(body)

    @classmethod
    async def delete_file(cls, name: str):
        assert name
        path = cls.get_path(name)
        try:
            await aiofiles.os.remove(path)
        except Exception as e:
            pass

    @classmethod
    def get_path(cls, name: str) -> str:
        path = os.path.join(cls.working_path(), name)
        return path


class PortPoolMixin:
    PORT_POOL: set[int] = set()
    LISTEN_POOL: set[int] = set()

    @classmethod
    def fill_port_pool(cls, port_begin: int, port_end: int):
        assert isinstance(port_begin, int)
        assert 0 < port_begin < 65536
        assert isinstance(port_end, int)
        assert 0 < port_end < 65536
        assert port_begin <= port_end
        for port in range(port_begin, port_end + 1):
            cls.PORT_POOL.add(port)

    def borrow_port(self) -> int:
        if not self.PORT_POOL:
            raise ValueError(f'无可用端口')
        return self.PORT_POOL.pop()

    def return_port(self, port: int):
        assert isinstance(port, int)
        self.PORT_POOL.add(port)


__all__ = [
    'QueueMixin',
    'HttpMixin',
    'SubscribeMixin',
    'StorageMixin',
    'TimerMixin',
    'PortPoolMixin',
]

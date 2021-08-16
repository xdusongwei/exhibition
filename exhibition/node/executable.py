import os
import re
import asyncio
import logging
from exhibition.base import *
from exhibition.message import *
from exhibition.mixin import *
from exhibition.process import *


class ExecutableNode(QueueMixin):
    def __init__(self, paths, store: QueueMixin) -> None:
        super().__init__()
        self.paths = paths or list()
        self.executables = list()
        self.store = store
        self.proc: Process = None
        self.obfs_local_path = None

    def __str__(self) -> str:
        return f'<ExecutableNode {id(self)} >'

    def __repr__(self) -> str:
        return self.__str__()

    async def stop(self):
        await super().stop()
        if self.proc:
            await self.proc.stop()
            self.proc = None

    @classmethod
    def find_obfs_plugin(cls) -> str:
        paths = os.environ['PATH']
        paths = paths.split(':')
        for path in paths:
            path = os.path.join(path, 'obfs-local')
            if os.path.isfile(path):
                return path
        return None

    async def create_executable(self, path: str) -> None | Executable:
        q = asyncio.Queue()
        self.proc = Process('test_executable', read_all=True, queue=q)
        await self.proc.start(path, '--help')
        await self.proc.wait(5)
        await self.proc.stop()
        self.proc = None
        executable = None
        version = None
        params = None
        obfs_plugin = None
        text = ''
        while not q.empty():
            m = await q.get()
            if m.action != ActionEnum.PROCESS_TEXT:
                continue
            text = m.readline
            if 'V2Ray' in text:
                executable = ExecutableEnum.V2RAY
                params = ['-version']
            if 'Xray' in text:
                executable = ExecutableEnum.XRAY
                params = ['-version']
            if 'shadowsocks' in text:
                executable = ExecutableEnum.SHADOWSOCKS
                obfs_plugin = self.obfs_local_path
        if not executable:
            return None
        if params:
            self.proc = Process('test_executable', read_all=True, queue=q)
            await self.proc.start(path, *params)
            await self.proc.wait(5)
            await self.proc.stop()
            self.proc = None
            while not q.empty():
                m = await q.get()
                if m.action != ActionEnum.PROCESS_TEXT:
                    continue
                text = m.readline
        match executable:
            case ExecutableEnum.V2RAY:
                if group := re.search(r'V2Ray\s(\S+)\s', text).groups():
                    version = group[0]
            case ExecutableEnum.XRAY:
                if group := re.search(r'Xray\s(\S+)\s', text).groups():
                    version = group[0]
            case ExecutableEnum.SHADOWSOCKS:
                if group := re.search(r'shadowsocks-libev\s(\S+)\s', text).groups():
                    version = group[0]
        return Executable(type=executable, version=version, path=path, obfs_plugin=obfs_plugin)

    async def update_executables(self):
        self.obfs_local_path = self.find_obfs_plugin()
        executables = list()
        for p in self.paths:
            try:
                executable = await self.create_executable(p)
                if executable:
                    executables.append(executable)
                else:
                    executables.append(Executable(type=None, version=None, path=p))
            except Exception as e:
                logging.error(f'探测可执行程序 {p} 出错:{e}')
        self.executables = executables
        logging.info(f'最新检测到的可执行程序:{executables}')

    async def on_start(self):
        self.action_timer(ActionEnum.EXECUTABLE_REFRESH, 1 * 60 * 60)
        await self.update_executables()
        self.store | Message(action=ActionEnum.EXECUTABLE_UPDATED)

    async def on_message(self, message: Message):
        match message.action:
            case ActionEnum.EXECUTABLE_REFRESH:
                self.action_timer(ActionEnum.EXECUTABLE_REFRESH, 12 * 60 * 60)

        match message.action:
            case ActionEnum.EXECUTABLE_CHANGED:
                self.paths = list(set(message.paths))

        match message.action:
            case ActionEnum.EXECUTABLE_REFRESH | ActionEnum.EXECUTABLE_CHANGED:
                await self.update_executables()
                self.store | Message(action=ActionEnum.EXECUTABLE_UPDATED)


__all__ = [
    'ExecutableNode',
]

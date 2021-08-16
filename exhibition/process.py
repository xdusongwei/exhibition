import logging
import shlex
import asyncio
from exhibition.base import *
from exhibition.message import *


class Process:
    def __init__(self, name, read_all=False, queue: asyncio.Queue = None):
        self.name = name
        self.queue = queue
        self.proc: asyncio.subprocess.Process = None
        self.stdout_task = None
        self.stderr_task = None
        self.read_all = read_all

    def __str__(self) -> str:
        pid = self.proc.pid if self.proc else None
        return f'<Process name:{self.name} pid:{pid} >'

    def __repr__(self) -> str:
        return self.__str__()

    @property
    def pid(self) -> None | int:
        if self.proc:
            return self.proc.pid
        return None

    async def start(self, *params):
        if self.proc:
            raise ValueError(f'存在进程')
        assert params
        args = shlex.split(' '.join(params))
        proc = await asyncio.create_subprocess_exec(
            *args,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        self.proc = proc
        msg = Message(
            action=ActionEnum.PROCESS_STARTED,
            name=self.name,
            process=self,
        )
        await self.queue.put(msg)
        self.stdout_task = asyncio.create_task(self.stdout_reader(), name=f'{self.name}.stdout.reader')
        self.stderr_task = asyncio.create_task(self.stderr_reader(), name=f'{self.name}.stderr.reader')

    async def stdout_reader(self):
        try:
            await self._pipe_reader(self.proc.stdout, StreamEnum.STDOUT)
        except asyncio.CancelledError:
            logging.debug(f'进程{self}被取消关注stdout')

    async def stderr_reader(self):
        try:
            await self._pipe_reader(self.proc.stderr, StreamEnum.STDERR)
        except asyncio.CancelledError:
            logging.debug(f'进程{self}被取消关注stderr')

    async def _pipe_reader(self, pipeline, stream):
        while True:
            if self.read_all:
                line = await pipeline.read()
            else:
                line = await pipeline.readline()
            if not line:
                msg = Message(
                    action=ActionEnum.PROCESS_EOF,
                    name=self.name,
                    process=self,
                    stream=stream,
                    readline=line,
                )
                await self.queue.put(msg)
                break
            try:
                line = line.decode('utf8')
            finally:
                msg = Message(
                    action=ActionEnum.PROCESS_TEXT,
                    name=self.name,
                    process=self,
                    stream=stream,
                    readline=line,
                )
                await self.queue.put(msg)

    async def wait(self, timeout: int=None) -> bool:
        if not self.proc:
            raise ValueError(f'缺失进程')
        try:
            await asyncio.wait_for(self.proc.wait(), timeout)
        except TimeoutError:
            return False
        return True

    async def stop(self):
        if not self.proc:
            return
        try:
            self.proc.terminate()
            self.proc = None
        except ProcessLookupError:
            pass
        finally:
            if self.stdout_task:
                self.stdout_task.cancel()
                await self.stdout_task
                self.stdout_task = None
            if self.stderr_task:
                self.stderr_task.cancel()
                await self.stderr_task
                self.stderr_task = None
            msg = Message(
                action=ActionEnum.PROCESS_STOPPED,
                name=self.name,
                process=self,
            )
            await self.queue.put(msg)


__all__ = [
    'Process',
]

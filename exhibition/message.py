import asyncio
from dataclasses import dataclass
from exhibition.base import *


@dataclass
class Message:
    action: ActionEnum
    name: str = None
    process: asyncio.subprocess.Process = None
    stream: StreamEnum = None
    readline: str = None
    export: 'ExportNode' = None
    airport: 'AirportNode' = None
    proxy: 'ProxyNode' = None
    paths: list[str] = None
    executable: 'ExecutableNode' = None
    executables: list['ExecutableNode'] = None
    nodes: dict[str, 'WorkingNode'] = None
    airports: dict[str, 'AirportNode'] = None
    custom: CustomNodeSettings = None
    queue: asyncio.Queue = None
    exception: tuple[Exception, list] = None
    from_timer: bool = False

    def __str__(self) -> str:
        return f'<Message {self.action} ' + \
               (f'name:{self.name} ' if self.name is not None else '') + \
               (f'process:{self.process} ' if self.process is not None else '') + \
               (f'stream:{self.stream} ' if self.stream is not None else '') + \
               (f'readline:{self.readline} ' if self.readline is not None else '') + \
               (f'export:{self.export} ' if self.export is not None else '') + \
               (f'airport:{self.airport} ' if self.airport is not None else '') + \
               (f'proxy:{self.proxy} ' if self.proxy is not None else '') + \
               (f'paths:{self.paths} ' if self.paths is not None else '') + \
               (f'executable:{self.executable} ' if self.executable is not None else '') + \
               (f'executables:{self.executables} ' if self.executables is not None else '') + \
               (f'nodes:{self.nodes} ' if self.nodes is not None else '') + \
               (f'custom:{self.custom} ' if self.custom is not None else '') + \
               (f'queue:{self.queue} ' if self.queue is not None else '') + \
               (f'fromTimer:{self.from_timer} ' if self.from_timer else '') + \
               (f'exception:{self.exception} ' if self.exception is not None else '') + \
               ' >'

    def __repr__(self) -> str:
        return self.__str__()


__all__ = [
    'Message',
]

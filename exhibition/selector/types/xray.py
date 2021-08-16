from exhibition.base import *
from exhibition.selector.types.v2ray import V2Ray


class XRay(V2Ray):
    EXECUTABLE_TYPE = ExecutableEnum.XRAY
    SUPPORT_INPUT = {
        ProxyEnum.VMESS,
        ProxyEnum.HTTP,
        ProxyEnum.SOCK5,
    }
    SUPPORT_OUTPUT = {
        ProxyEnum.VMESS,
        ProxyEnum.SOCK5,
    }

    def config_filename(self, name: str) -> str:
        return f'{name}.json'

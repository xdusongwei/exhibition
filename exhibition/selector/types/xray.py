from exhibition.base import *
from exhibition.selector.types.v2ray import V2Ray


class XRay(V2Ray):
    EXECUTABLE_TYPE = ExecutableEnum.XRAY
    SUPPORT_INPUT = {
        ProxyEnum.VLESS,
        ProxyEnum.VMESS,
        ProxyEnum.HTTP,
        ProxyEnum.SOCKS5,
        ProxyEnum.SHADOWSOCKS,
    }
    SUPPORT_OUTPUT = {
        ProxyEnum.VMESS,
        ProxyEnum.SOCKS5,
    }

    def config_filename(self, name: str) -> str:
        return f'{name}.json'

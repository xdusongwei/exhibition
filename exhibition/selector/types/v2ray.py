import json
from exhibition.base import *
from exhibition.selector.types.abstract import ExecutableAbstract


class V2Ray(ExecutableAbstract):
    EXECUTABLE_TYPE = ExecutableEnum.V2RAY
    SUPPORT_INPUT = {
        ProxyEnum.VMESS,
        ProxyEnum.HTTP,
        ProxyEnum.SOCK5,
    }
    SUPPORT_OUTPUT = {
        ProxyEnum.VMESS,
        ProxyEnum.SOCK5,
        ProxyEnum.HTTP,
    }

    def config_filename(self, name: str) -> str:
        return f'{name}.json'

    def process_args(self, config_path: str) -> list[str]:
        return [self.executable.path, '-c', config_path, ]

    def export_config(
            self,
            export_settings: ExportSettings,
            working_settings: list[tuple[WorkingNodeState, WorkingNodeSettings]],
    ):
        match export_settings.proxy:
            case ProxyEnum.VMESS | ProxyEnum.VLESS:
                protocol = None
                match export_settings.proxy:
                    case ProxyEnum.VMESS:
                        protocol = 'vmess'
                    case ProxyEnum.VLESS:
                        protocol = 'vless'
                network = self.obfuscating_to_network(export_settings)
                inbound = {
                    'listen': export_settings.host,
                    'port': export_settings.port,
                    'protocol': protocol,
                    'tag': export_settings.id,
                    'settings': {
                        'clients': [
                            {
                                'alterId': export_settings.alter_id,
                                'email': export_settings.id,
                                'id': export_settings.uuid,
                                'level': 0,
                                'flow': export_settings.flow,
                            },
                        ],
                        'default': {
                            'alterId': export_settings.alter_id,
                            'level': 0,
                        },
                    },
                    'streamSettings': {
                        'network': network,
                        'security': export_settings.security,
                        'tlsSettings': {
                            'usage': export_settings.usage,
                            'keyFile': export_settings.key_file,
                            'certificateFile': export_settings.certificate_file,
                        },
                        'tcpSettings': {

                        },
                        'wsSettings': {
                            'path': export_settings.path,
                        } if export_settings.obfuscating == ObfuscatingEnum.WEBSOCKET else None,
                        'httpSettings': {

                        } if export_settings.obfuscating == ObfuscatingEnum.HTTP2 else None,
                        'quicSettings': {

                        },
                        'grpcSettings': {

                        },
                    }
                }
            case ProxyEnum.HTTP:
                inbound = {
                    'listen': export_settings.host,
                    'port': export_settings.port,
                    'protocol': 'http',
                    'tag': export_settings.id,
                    'settings': {
                        'accounts': [
                            {
                                'user': user,
                                'pass': password,
                            } for user, password in export_settings.account_list or list()],
                        'allowTransparent': False,
                        'userLevel': 0,
                    },
                }
            case ProxyEnum.SOCK5:
                inbound = {
                    'listen': export_settings.host,
                    'port': export_settings.port,
                    'protocol': 'socks',
                    'tag': export_settings.id,
                    'settings': {
                        'auth': 'password' if export_settings.account_list else 'noauth',
                        'accounts': [
                            {
                                'user': user,
                                'pass': password,
                            } for user, password in export_settings.account_list or list()
                        ],
                        "udp": False,
                        "userLevel": 0,
                    },
                }
            case _:
                raise ValueError(f'{self}不支持{export_settings.proxy}作为外露服务协议')
        outbounds = [
            {
                'protocol': 'freedom',
                'settings': {

                },
                'streamSettings': None,
                'tag': 'direct',
            }
        ]
        for state, settings in working_settings:
            match state.proxy:
                case ProxyEnum.SOCK5:
                    outbound = {
                        'tag': settings.id,
                        'protocol': 'socks',
                        'settings': {
                            'servers': [
                                {
                                    'address': state.host,
                                    'port': state.port,
                                },
                            ],
                        },
                    }
                case _:
                    raise ValueError(f'{self}不支持{state.proxy}作为外露服务与工作节点通信的协议')
            outbounds.append(outbound)

        config = {
            'inbounds': [
                inbound,
            ],
            'outbounds': outbounds,
            'routing': {
                'balancers': [
                    {
                        'selector': [settings.id for _, settings in working_settings],
                        'tag': 'proxy',
                    }
                ],
                'rules': [
                    {
                        'ip': [
                            'geoip:private',
                            'geoip:cn',
                        ],
                        'domain': [
                            'geosite:cn',
                        ],
                        'outboundTag': 'direct',
                        'type': 'field',
                    },
                    {
                        'balancerTag': 'proxy',
                        'network': 'tcp,udp',
                        'type': 'field',
                    }
                ]
            }
        }
        return json.dumps(config, indent=2)

    def working_config(
            self,
            statue: WorkingNodeState,
            settings: WorkingNodeSettings,
    ):
        match statue.proxy:
            case ProxyEnum.SOCK5:
                inbound = {
                    'listen': statue.host,
                    'port': statue.port,
                    'protocol': 'socks',
                    'tag': settings.id,
                    'settings': {
                        'auth': 'noauth',
                    },
                }
            case _:
                raise ValueError(f'{self}不支持{statue.proxy}作为工作节点协议')
        match settings.proxy:
            case ProxyEnum.VLESS:
                network = self.obfuscating_to_network(settings)
                outbound = {
                    'tag': settings.id,
                    'protocol': 'vless',
                    'settings': {
                        'vnext': [
                            {
                                'address': settings.host,
                                'port': settings.port,
                                'users': [
                                    {
                                        'id': settings.uuid,
                                        'encryption': settings.encryption,
                                        'flow': settings.flow,
                                        'level': 0,
                                    },
                                ],
                            },
                        ],
                    },
                    'streamSettings': {
                        'network': network,
                        'security': settings.security,
                        'tlsSettings': {
                            'usage': settings.usage,
                            'keyFile': settings.key_file,
                            'certificateFile': settings.certificate_file,
                        },
                        'tcpSettings': {},
                        'wsSettings': {
                            'path': settings.path,
                        } if settings.obfuscating == ObfuscatingEnum.WEBSOCKET else None,
                        'httpSettings': {

                        } if settings.obfuscating == ObfuscatingEnum.HTTP2 else None,
                        'quicSettings': {},
                        'grpcSettings': {},
                        'sockopt': {},
                    }
                }
            case ProxyEnum.VMESS:
                network = self.obfuscating_to_network(settings)
                outbound = {
                    'tag': settings.id,
                    'protocol': 'vmess',
                    'settings': {
                        'vnext': [
                            {
                                'address': settings.host,
                                'port': settings.port,
                                'users': [
                                    {
                                        'alterId': settings.alter_id,
                                        'id': settings.uuid,
                                        'level': 0,
                                    },
                                ],
                            },
                        ],
                    },
                    'streamSettings': {
                        'network': network,
                        'security': settings.security,
                        'tlsSettings': {},
                        'tcpSettings': {},
                        'wsSettings': {
                            'path': settings.path,
                        } if settings.obfuscating == ObfuscatingEnum.WEBSOCKET else None,
                        'httpSettings': {

                        } if settings.obfuscating == ObfuscatingEnum.HTTP2 else None,
                        'quicSettings': {},
                        'grpcSettings': {},
                        'sockopt': {},
                    }
                }
            case ProxyEnum.SOCK5:
                outbound = {
                    'tag': settings.id,
                    'protocol': 'socks',
                    'settings': {
                        'servers': [{
                            'address': settings.host,
                            'port': settings.port,
                            'users': [
                                {
                                    'user': settings.user,
                                    'pass': settings.password,
                                    'level': 0
                                }
                            ] if settings.user else None
                        }]
                    },
                }
            case ProxyEnum.HTTP:
                outbound = {
                    'tag': settings.id,
                    'protocol': 'http',
                    'settings': {
                        'servers': [{
                            'address': settings.host,
                            'port': settings.port,
                            'users': [
                                {
                                    'user': settings.user,
                                    'pass': settings.password,
                                    'level': 0
                                }
                            ] if settings.user else None
                        }]
                    },
                }
            case _:
                raise ValueError(f'{self}不支持{settings.proxy}作为工作节点通信的远端协议')

        config = {
            "inbounds": [
                inbound,
            ],
            "outbounds": [
                outbound,
            ],
        }
        return json.dumps(config, indent=2)

    @classmethod
    def obfuscating_to_network(cls, settings: BaseNodeSettings | ExportSettings) -> str:
        if isinstance(settings, BaseNodeSettings):
            obfuscating = settings.obfuscating
        elif isinstance(settings, ExportSettings):
            obfuscating = settings.obfuscating
        else:
            raise ValueError(f'不能判断network的配置:{settings}')
        match obfuscating:
            case None:
                return 'tcp'
            case ObfuscatingEnum.WEBSOCKET:
                return 'ws'
            case ObfuscatingEnum.HTTP2:
                return 'http'
            case _:
                raise ValueError(f'不能处理的混淆类型:{settings.obfuscating}')

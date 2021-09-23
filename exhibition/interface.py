import os
from uuid import uuid4
from aiohttp import web
from exhibition.base import *
from exhibition.message import *
from exhibition.node import *
from exhibition.store import Store


routes = web.RouteTableDef()


@routes.view("/")
class RootView(web.View):
    async def get(self):
        return web.HTTPFound('./index.html')


class ApiView(web.View):
    async def body_dict(self) -> dict:
        d = await self.request.json()
        return d

    @property
    def store(self) -> Store:
        return getattr(self.request.app, '_store')


@routes.view("/interface/executables")
class ExecutableView(ApiView):
    async def change_paths(self, paths):
        message = Message(action=ActionEnum.EXECUTABLE_CHANGED, paths=paths)
        self.store.executable_node | message
        return message

    async def get(self):
        executables = self.store.executables
        items = [i.to_dict() for i in executables]
        response = {
            'executables': items,
        }
        return web.json_response(response)

    async def put(self):
        args = await self.body_dict()
        path = args.get('path')
        if not path:
            return web.json_response(
                data={
                    'error': '参数不正确',
                },
                status=400,
            )
        if any([i for i in self.store.executable_paths if i == path]):
            return web.json_response(
                data={
                    'error': f'{path} 已经创建过',
                },
                status=400,
            )
        if not os.path.isfile(path):
            return web.json_response(
                data={
                    'error': f'{path} 不是有效文件',
                },
                status=400,
            )
        paths = self.store.executable_paths.copy()
        paths.append(path)
        message = await self.change_paths(paths)
        return web.json_response(
            data={
                'message': str(message),
            },
        )

    async def post(self):
        args = await self.body_dict()
        path = args.get('path')
        new_path = args.get('newPath')
        if not path or not new_path or path == new_path:
            return web.json_response(
                data={
                    'error': '参数不正确',
                },
                status=400,
            )
        if any([i for i in self.store.executable_paths if i == new_path]):
            return web.json_response(
                data={
                    'error': f'{new_path} 已经创建过',
                },
                status=400,
            )
        if not os.path.isfile(new_path):
            return web.json_response(
                data={
                    'error': f'{new_path} 不是有效文件',
                },
                status=400,
            )
        paths = self.store.executable_paths.copy()
        paths.remove(path)
        paths.append(new_path)
        message = await self.change_paths(paths)
        return web.json_response(
            data={
                'message': str(message),
            },
        )

    async def delete(self):
        args = await self.body_dict()
        path = args.get('path')
        if not path:
            return web.json_response(
                data={
                    'error': '参数不正确',
                },
                status=400,
            )
        if not any([i for i in self.store.executable_paths if i == path]):
            return web.json_response(
                data={
                    'error': f'不存在位置项目: {path}',
                },
                status=400,
            )
        paths = self.store.executable_paths.copy()
        paths.remove(path)
        message = await self.change_paths(paths)
        return web.json_response(
            data={
                'message': str(message),
            },
        )


@routes.view("/interface/airport")
class AirportNodeView(ApiView):
    async def get(self):
        nodes = self.store.airport_nodes
        items = list()
        for node in nodes.values():
            item = node.to_dict()
            usability = 0
            node_count = node.node_count
            for working_node in self.store.working_nodes.values():
                if working_node.settings.airport_id != node.settings.id:
                    continue
                if working_node.is_outdated:
                    continue
                if working_node.state.speed:
                    usability += 1
            if node_count:
                usability = '{0:.1f}'.format(100.0 * usability / node_count)
            else:
                usability = '--'
            item['usability'] = usability
            items.append(item)

        response = {
            'airportNodes': items,
        }
        return web.json_response(response)

    async def put(self):
        args = await self.body_dict()
        name = args.get('name')
        url = args.get('url')
        exclude_regex = args.get('excludeRegex') or None
        if not name or not url:
            return web.json_response(
                data={
                    'error': '参数不正确',
                },
                status=400,
            )
        airport_id = generate_hash('AP', name, url)
        if airport_id in self.store.airport_nodes:
            return web.json_response(
                data={
                    'error': '机场设置重复',
                },
                status=400,
            )
        settings = AirportSettings(
            id=airport_id,
            name=name,
            url=url,
            exclude_regex=exclude_regex,
        )
        airport = AirportNode(settings=settings, store=self.store)
        message = Message(action=ActionEnum.AIRPORT_UPDATED, airport=airport)
        self.store | message
        return web.json_response(
            data={
                'airportId': airport_id,
            },
        )

    async def delete(self):
        args = await self.body_dict()
        airport_id = args.get('airportId')
        if not airport_id:
            return web.json_response(
                data={
                    'error': '参数不正确',
                },
                status=400,
            )
        if airport_id not in self.store.airport_nodes:
            return web.json_response(
                data={
                    'error': '不存在机场配置',
                },
                status=400,
            )
        airport = self.store.airport_nodes[airport_id]
        message = Message(action=ActionEnum.AIRPORT_REMOVE, airport=airport)
        self.store | message
        return web.json_response(
            data={
                'airportId': airport_id,
            },
        )


@routes.view("/interface/airport/refresh")
class AirportNodeRefreshView(ApiView):
    async def post(self):
        args = await self.body_dict()
        airport_id = args.get('airportId')
        if not airport_id:
            return web.json_response(
                data={
                    'error': '参数不正确',
                },
                status=400,
            )
        if airport_id not in self.store.airport_nodes:
            return web.json_response(
                data={
                    'error': '不存在机场配置',
                },
                status=400,
            )
        airport = self.store.airport_nodes[airport_id]
        message = Message(action=ActionEnum.AIRPORT_SUBSCRIBE)
        airport | message

        response = {
            'airportId': airport_id,
        }
        return web.json_response(response)


@routes.view("/interface/working")
class WorkingNodeView(ApiView):
    async def get(self):
        nodes = self.store.working_nodes
        items = list()
        for node in nodes.values():
            item = node.to_dict()
            airport_id = node.settings.airport_id
            airport = self.store.airport_nodes.get(airport_id)
            if airport:
                item['airport'] = airport.to_dict()
            items.append(item)
        response = {
            'workingNodes': items,
        }
        return web.json_response(response)


@routes.view("/interface/working/test")
class WorkingNodeTestView(ApiView):
    async def post(self):
        args = await self.body_dict()
        working_id = args.get('workingId')
        if not working_id:
            for node in self.store.working_nodes.values():
                node | Message(action=ActionEnum.WORKING_LATENCY_TEST)
        elif working_id not in self.store.working_nodes:
            return web.json_response(
                data={
                    'error': f'{working_id}不存在',
                },
                status=400,
            )
        else:
            self.store.working_nodes[working_id] | Message(action=ActionEnum.WORKING_LATENCY_TEST)
        response = {
            'workingId': working_id,
        }
        return web.json_response(response)


@routes.view("/interface/export")
class ExportNodeView(ApiView):
    async def get(self):
        nodes = self.store.export_nodes
        items = [i.to_dict() for i in nodes]
        response = {
            'exportNodes': items,
        }
        return web.json_response(response)

    async def put(self):
        args = await self.body_dict()
        name = args.get('name')
        assert name
        proxy = args.get('proxy')
        proxy = ProxyEnum[proxy]
        host = args.get('host')
        port = args.get('port')
        port = int(port)
        assert 0 < port <= 65536
        obfuscating = args.get('obfuscating')
        obfuscating = ObfuscatingEnum[obfuscating] if obfuscating else None
        path = args.get('path')
        alter_id = args.get('alterId')
        uuid = args.get('uuid')
        security = args.get('security') or None
        usage = args.get('usage') or None
        key_file = args.get('keyFile') or None
        certificate_file = args.get('certificateFile') or None
        flow = args.get('flow') or None
        select_count = args.get('selectCount')
        select_count = int(select_count)
        assert select_count > 0
        include_airport_name_regex = args.get('includeAirportNameRegex')
        include_working_name_regex = args.get('includeWorkingNameRegex')
        exclude_airport_name_regex = args.get('excludeAirportNameRegex')
        exclude_working_name_regex = args.get('excludeWorkingNameRegex')
        method = args.get('method')
        user = args.get('user')
        password = args.get('password')
        account_list = None
        match proxy:
            case ProxyEnum.SOCKS5 | ProxyEnum.HTTP:
                if (not user and password) or (user and not password):
                    return web.json_response(
                        data={
                            'error': '需要同时填写用户密码',
                        },
                        status=400,
                    )
                else:
                    account_list = [[user, password, ], ]
            case ProxyEnum.SHADOWSOCKS:
                if (not method and password) or (method and not password):
                    return web.json_response(
                        data={
                            'error': '需要同时填写method和密码',
                        },
                        status=400,
                    )
                else:
                    account_list = [[method, password, ], ]

        export_id = generate_hash('EP', uuid4().hex)
        settings = ExportSettings(
            id=export_id,
            name=name,
            proxy=proxy,
            host=host,
            port=port,
            obfuscating=obfuscating,
            path=path,
            alter_id=alter_id,
            uuid=uuid,
            security=security,
            usage=usage,
            key_file=key_file,
            certificate_file=certificate_file,
            flow=flow,
            select_count=select_count,
            include_airport_name_regex=include_airport_name_regex,
            include_working_name_regex=include_working_name_regex,
            exclude_airport_name_regex=exclude_airport_name_regex,
            exclude_working_name_regex=exclude_working_name_regex,
            account_list=account_list,
        )
        node = ExportNode(settings=settings, config_settings=lambda :self.store.settings)
        message = Message(action=ActionEnum.EXPORT_UPDATE, export=node)
        self.store | message
        return web.json_response(
            data={
                'exportId': export_id,
            },
        )

    async def delete(self):
        args = await self.body_dict()
        export_id = args.get('exportId')
        for node in self.store.export_nodes:
            if node.settings.id != export_id:
                continue
            message = Message(action=ActionEnum.EXPORT_REMOVE, export=node)
            self.store | message
            break
        else:
            return web.json_response(
                data={
                    'error': '不存在外露服务配置',
                },
                status=400,
            )
        return web.json_response(
            data={
                'exportId': export_id,
            },
        )


@routes.view("/interface/export/select")
class ExportNodeSelectView(ApiView):
    async def post(self):
        args = await self.body_dict()
        export_id = args.get('exportId')
        for node in self.store.export_nodes:
            if node.settings.id != export_id:
                continue
            message = Message(action=ActionEnum.EXPORT_REFRESH)
            node | message
            break
        else:
            return web.json_response(
                data={
                    'error': '不存在外露服务配置',
                },
                status=400,
            )
        return web.json_response(
            data={
                'exportId': export_id,
            },
        )


@routes.view("/interface/node")
class CustomNodeView(ApiView):
    async def get(self):
        nodes = self.store.custom_nodes
        items = [i.to_dict() for i in nodes]
        response = {
            'customNodes': items,
        }
        return web.json_response(response)

    async def put(self):
        args = await self.body_dict()
        name = args.get('name')
        assert name
        proxy = args.get('proxy')
        proxy = ProxyEnum[proxy]
        host = args.get('host')
        port = args.get('port')
        port = int(port)
        assert 0 < port <= 65536
        obfuscating = args.get('obfuscating')
        obfuscating = ObfuscatingEnum[obfuscating] if obfuscating else None
        tls = args.get('tls')
        path = args.get('path')
        alter_id = args.get('alterId')
        uuid = args.get('uuid')
        security = args.get('security')
        encryption = args.get('encryption')
        flow = args.get('flow')
        encrypt_method = args.get('encryptMethod')
        user = args.get('user')
        password = args.get('password')
        node_id = generate_hash('NC', uuid4().hex)
        settings = CustomNodeSettings(
            id=node_id,
            name=name,
            proxy=proxy,
            host=host,
            port=port,
            obfuscating=obfuscating,
            tls=tls,
            path=path,
            alter_id=alter_id,
            uuid=uuid,
            security=security,
            encryption=encryption,
            flow=flow,
            encrypt_method=encrypt_method,
            user=user,
            password=password,
        )
        message = Message(action=ActionEnum.CUSTOM_NODE_UPDATED, custom=settings)
        self.store | message
        return web.json_response(
            data={
                'nodeId': node_id,
            },
        )

    async def delete(self):
        args = await self.body_dict()
        node_id = args.get('nodeId')
        for node in self.store.custom_nodes:
            if node.id != node_id:
                continue
            message = Message(action=ActionEnum.CUSTOM_NODE_REMOVE, custom=node)
            self.store | message
            return web.json_response(
                data={
                    'nodeId': node_id,
                },
            )
        else:
            return web.json_response(
                data={
                    'error': f'不存在自定义节点{node_id}的配置',
                },
                status=400,
            )


@routes.view("/interface/settings")
class SettingsView(ApiView):
    async def get(self):
        settings = self.store.settings
        return web.json_response(
            data={
                'settings': settings.to_dict(),
            },
        )

    async def post(self):
        args = await self.body_dict()
        settings = self.store.settings
        should_reset_working_pool = settings.update(args)
        self.store | Message(action=ActionEnum.STORE_SAVE_SETTINGS)
        return web.json_response(
            data={
                'settings': settings.to_dict(),
            },
        )


__all__ = [
    'routes',
]

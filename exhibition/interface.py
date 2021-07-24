import os
from aiohttp import web
from exhibition.base import *
from exhibition.message import *
from exhibition.node import *
from exhibition.store import Store


routes = web.RouteTableDef()


@routes.view("/")
class RootView(web.View):
    async def get(self):
        return web.HTTPFound('/index.html')


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
        await self.store.executable_node.queue.put(message)
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
            for working_node in self.store.nodes.values():
                if working_node.settings.airport_id != node.settings.id:
                    continue
                if working_node.is_outdated:
                    continue
                if working_node.speed:
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
        )
        airport = AirportNode(settings, self.store.queue)
        message = Message(action=ActionEnum.AIRPORT_UPDATED, airport=airport)
        await self.store.queue.put(message)
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
        await self.store.queue.put(message)
        return web.json_response(
            data={
                'airportId': airport_id,
            },
        )


@routes.view("/interface/working")
class WorkingNodeView(ApiView):
    async def get(self):
        nodes = self.store.nodes
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


@routes.view("/interface/export")
class ExportNodeView(ApiView):
    async def get(self):
        nodes = self.store.export_nodes
        items = [i.to_dict() for i in nodes]
        response = {
            'exportNodes': items,
        }
        return web.json_response(response)


__all__ = [
    'routes',
]

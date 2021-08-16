import os
import sys
import asyncio
import logging
import argparse
from aiohttp import web
from exhibition.store import Store
from exhibition.interface import routes


def change_legacy():
    legacy_gather = asyncio.gather
    async def gather(*coros_or_futures, loop=None, return_exceptions=False):
        return await legacy_gather(*coros_or_futures, return_exceptions=return_exceptions)
    asyncio.gather = gather


def locate_web_path():
    current_path = __file__
    current_dir = os.path.dirname(current_path)
    return os.path.join(current_dir, 'www')


def setup_log(loglevel):
    handler = logging.StreamHandler(stream=sys.stdout)
    fmt = '%(asctime)s %(levelname)s:%(message)s'
    formatter = logging.Formatter(fmt, datefmt='%m-%d %H:%M:%S')
    handler.setFormatter(formatter)
    logging.getLogger().addHandler(handler)
    logging.getLogger().setLevel(logging.getLevelName(loglevel))


async def on_start(app):
    args = getattr(app, 'args')
    setup_log(args.loglevel)

    store: Store = getattr(app, '_store')
    await store.spawn()


async def on_shutdown(app):
    store: Store = getattr(app, '_store')
    await store.stop()
    delattr(app, '_store')


def main():
    welcome = "exhibition"
    parser = argparse.ArgumentParser(description=welcome)
    parser.add_argument(
        '--host',
        default='0.0.0.0',
        help='web服务监听地址，默认0.0.0.0',
    )
    parser.add_argument(
        '--port',
        default=8080,
        help='web服务监听端口，默认8080',
        type=int,
    )
    parser.add_argument(
        '--loglevel',
        default='INFO',
        help='日志等级，默认INFO',
    )
    parser.add_argument(
        '--accesslog',
        action='store_true',
        help='是否打印web服务器的访问日志',
    )
    args = parser.parse_args()
    host = args.host
    port = args.port

    store = Store()
    change_legacy()
    app = web.Application()
    setattr(app, 'args', args)
    app.add_routes(routes)
    app.add_routes([
        web.static('/', locate_web_path()),
    ])
    setattr(app, '_store', store)
    app.on_startup.append(on_start)
    app.on_cleanup.append(on_shutdown)
    app_args = {
        'app': app,
        'host': host,
        'port': port,
    }
    if not args.accesslog:
        app_args['access_log'] = None
    web.run_app(**app_args)


if __name__ == '__main__':
    main()

import argparse
import asyncio
from cache import Cache
from server import CachingProxy

import logging

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Caching proxy server')
    parser.add_argument('--host', default='localhost', help='Host to bind the proxy server')
    parser.add_argument('--port', help='port for proxy server.', type=int)
    parser.add_argument('--origin', help='Origin server URL.')
    parser.add_argument('--clear-cache', action="store_true", help='clear all cached requests.')

    parser.add_argument('--cache-port', default=6379 ,help='Redis cache host.', type=int)
    parser.add_argument('--cache-host', default='localhost' ,help='Redis cache port.')

    logging.basicConfig(
        format="{asctime} - {levelname} - {message}",
        style="{",
        datefmt="%Y-%m-%d %H:%M",
        level=logging.INFO
    )
    logger = logging.getLogger(__name__)

    args = parser.parse_args()

    cache = Cache(host=args.cache_host, port=args.cache_port)

    if args.clear_cache:
        cache.clear()
        logger.info("Cache cleared")
    else:
        caching_proxy = CachingProxy(port=args.port, origin=args.origin, cache=cache)
        asyncio.run(caching_proxy.run(args.host))
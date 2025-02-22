import asyncio
import aiohttp
from typing import Dict
import logging
from cache import Cache

logger = logging.getLogger(__name__)

class CachingProxy:
    def __init__(self, port, origin, cache: Cache):
        self.port = port
        self.origin = origin
        self.cache = cache

    def _build_response_dict(self, response: aiohttp.ClientResponse, body: bytes):
        return {
            'status': response.status,
            'headers': dict(response.headers),
            'body': body.decode()
            }
        

    def _format_http_response(self, response: Dict):
        return (
            f"HTTP/1.1 {response['status']} OK\r\n"
            f"{response['headers']}\r\n\r\n"
            f"{response['body']}"
        ).encode('utf-8')
        
    async def do_GET(self, url, path):
        cached_response = self.cache.get(path)

        if cached_response:
            cached_response['headers']['X-Cache'] = 'HIT'
            logger.info(f'Cache Hit for {path}')

            return cached_response

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:

                    body = await response.read()
                    data = self._build_response_dict(response, body)

                    self.cache.set(path, data)
                    data['headers']['X-Cache'] = 'MISS'
                    logger.info(f'Cache Miss for {path}')
                    return data
        except aiohttp.ClientError as e:
            logger.error(f'reqeust to {url} failed')
            return {
                'status': 502,
                'headers': {'Content-Type': 'text/plain'},
                'body': 'Bad Gateway'
            }

    
    def _parse_url(self, url):
        """Example: 
            GET /get HTTP/1.1
            Host: localhost:3000
            User-Agent: curl/8.5.0
            Accept: */*
        """
        try:
            method, path, _ = url.split(' ', 2)
            if not method == 'GET':
                return {'status': 405, 'headers': {'Content-Type': 'text/plain'}, 'body': 'Method Not Allowed'}

            return {'path':path}
        except Exception as e:
            logger.error(f'error parsing url: {e}')
            return None
    

    async def handle_client(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        addr = writer.get_extra_info('peername')
        logger.info(f'Connected to {addr}')

        try:
            while True:
                data = await reader.read(1024)
                if not data:
                    break

                parsed_url = self._parse_url(data.decode('utf-8', errors='ignore'))
                if not parsed_url or 'status' in parsed_url:
                    response = {'status': 400, 'headers': {}, 'body': 'Bad Request'}
                    writer.write(self._format_http_response(response))
                    await writer.drain()
                    break

                url = f'{self.origin}{parsed_url['path']}'
                response = await self.do_GET(url, parsed_url['path'])
                writer.write(self._format_http_response(response))
                await writer.drain()

        except Exception as e:
            logger.error(f'error handeling cilent {addr}: {e}')

        finally:
            writer.close()
            await writer.wait_closed()
            logger.info(f'Diconnected from {addr}')

    
    async def run(self, host):
        server = await asyncio.start_server(
            self.handle_client, host, self.port
        )

        logger.info(f"Proxy server running on {host}:{self.port}, forwarding to {self.origin}")
        async with server:
            await server.serve_forever()

            



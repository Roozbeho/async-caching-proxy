# Async Caching Proxy Server

A high-performance, asynchronous caching proxy server built with Python, `asyncio`, `aiohttp`, and Redis. This proxy enhances efficiency by caching HTTP GET responses, reducing redundant network requests, and accelerating response times.

## Features
- **Redis-based caching** to minimize redundant requests
- **Asynchronous handling** with `aiohttp` for high performance
- **Logs cache hits/misses** with `X-Cache` headers
- **Supports clearing cache** via command-line arguments

## Requirements

- Python 3.7+
- Redis Server
- Required Python Packages:
  - `aiohttp`
  - `asyncio`
  - `redis`

## Installation

1. Clone the repository:
   ```sh
   git clone https://github.com/Roozbeho/caching-proxy.git
   cd caching-proxy
   ```

2. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```

3. Start Redis server (if not already running):
   ```sh
   redis-server
   ```

## Usage

Run the proxy server with the following command:

```sh
python main.py --host localhost --port 3000 --origin http://example.com
```

### Available Arguments
| Argument        | Description                                 | Default       |
|-----------------|---------------------------------------------|---------------|
| `--host`        | Host to bind the proxy server               | `localhost`   |
| `--port`        | Port for the proxy server                   | Required      |
| `--origin`      | The origin server URL to forward requests   | Required      |
| `--clear-cache` | Clears all cached requests                  | Disabled      |
| `--cache-host`  | Redis cache host                            | `localhost`   |
| `--cache-port`  | Redis cache port                            | `6379`        |

### Example Request
Once the proxy server is running, you can make a request:
```sh
curl -v http://localhost:3000/products
```
If the response is cached, the response headers will include `X-Cache: HIT`. Otherwise, `X-Cache: MISS` will be added.

### Clear Cache
To clear the cache before running the server, use:
```sh
python main.py --clear-cache
```



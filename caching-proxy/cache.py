import redis
import json

class Cache:
    def __init__(self, host='localhost', port=6379):
        self.r = redis.Redis(host=host, port=port, db=0)

    def _generate_unique_key(self, url_path):
        return f'response-{url_path}'

    def get(self, url_path):
        url_path_key = self._generate_unique_key(url_path)
        cached_response = self.r.get(url_path_key)
        if cached_response:
            return json.loads(cached_response)
        
        return None
    
    def set(self, url_path, data):
        url_path_key = self._generate_unique_key(url_path)
        self.r.set(url_path_key, json.dumps(data))

        return data
    
    def clear(self):
        self.r.flushall()
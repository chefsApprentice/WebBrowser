import time;
import heapq


class HtmlTimeCache:
    def __init__(self):
        self.cache = {}
        self.expiry_queue = []

    def set(self, key, value, ttl):
        expiry = time.time() + ttl
        self.cache[key] = (value, expiry)
        heapq.heappush(self.expiry_queue, (expiry, key))

    def get(self, key):
        self.evict_expired()
        if key in self.cache:
            return self.cache[key][0]
        return None

    def evict_expired(self):
        now = time.time()
        while self.expiry_queue and self.expiry_queue[0][0] <= now:
            expiry, key = heapq.heappop(self.expiry_queue)
            if key in self.cache and self.cache[key][1] <= now:
                del self.cache[key]


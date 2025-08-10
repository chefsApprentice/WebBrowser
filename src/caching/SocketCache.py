from collections import OrderedDict


class socketCache:
    def __init__(self, maxSize = 1):
        self.maxSize=maxSize;
        self.cache = OrderedDict();

    def get(self, key):
        return self.cache.get(key);

    def add(self, key, value):
        if key in self.cache:
            self.cache.move_to_end(key);
        self.cache[key] = value;
        if len(self.cache) > self.maxSize:
            key2, val = self.cache.popitem(last=False)
            val.close();
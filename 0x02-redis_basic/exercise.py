#!/usr/bin/env python3
"""Writing strings to Redis"""
import redis
from uuid import uuid4
from typing import Union, Callable, Optional
from functools import wraps


def count_calls(method: Callable) -> Callable:
    """
    count how many times methods of the Cache class are called.
    """
    @wraps(method)
    def wrapper(self, *args, **kwargs):
        """Wrapper function"""
        self._redis.incr(method.__qualname__)
        return method(self, *args, **kwargs)
    return wrapper


def call_history(method: Callable) -> Callable:
    """
    store the history of inputs and outputs for a particular function.
    """
    @wraps(method)
    def wrapper(self, *args, **kwargs):
        """Wrapper function"""
        input = str(args)
        self._redis.rpush(method.__qualname__ + ":inputs", input)
        output = str(method(self, *args, **kwargs))
        self._redis.rpush(method.__qualname__ + ":outputs", output)
        return output
    return wrapper


def replay(method: Callable) -> None:
    """
     function to display the history of calls of a particular function
    """
    r = redis.Redis()
    name = method.__qualname__
    count = r.get(name).decode('utf-8')
    inputs = r.lrange(name + ":inputs", 0, -1)
    outputs = r.lrange(name + ":outputs", 0, -1)
    print("{} was called {} times:".format(name, count))
    for i, o in zip(inputs, outputs):
        print("{}(*{}) -> {}".format(name, i.decode('utf-8'),
                                     o.decode('utf-8')))

class Cache:
    """Redis cache class"""
    
    def __init__(self):
        """Initiiates a Redis client"""
        self._redis = redis.Redis()
        self._redis.flushdb()
    
    @count_calls
    @call_history
    def store(self, data: Union[str, bytes, int, float]) -> str:
        """Stores data in Redis and returns a key"""
        key = str(uuid4())
        self._redis.set(key, data)
        return key
    
    def get(self, key: str, fn: Optional[Callable] = None) -> Union[str, bytes, int, float, None]:
        """Gets value from Redis using key"""
        data = self._redis.get(key)
        if not data:
            return None
        return fn(data) if fn else data
    
    def get_str(self, key: str) -> str:
        """Converts bytes to str"""
        return self.get(key, lambda x: x.decode('utf-8'))
    
    def get_int(self, key: str) -> int:
        """Converts bytes to int"""
        return self.get(key, int)
# web.py
import requests
import redis
from functools import wraps
from typing import Callable


def cache_with_expiry(expiration_seconds: int):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            url = args[0]
            cache_key = f"cache:{url}"

            # Check if the result is in the cache
            cached_result = redis_client.get(cache_key)
            if cached_result:
                # If cached result exists, return it
                print(f"Cache hit for {url}")
                return cached_result.decode("utf-8")

            # If not in cache, execute the function to get the result
            result = func(*args, **kwargs)

            # Store the result in the cache with expiration time
            redis_client.setex(cache_key, expiration_seconds, result)

            return result
        return wrapper
    return decorator


def track_access_count(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        url = args[0]
        count_key = f"count:{url}"

        # Increment the access count
        access_count = redis_client.incr(count_key)

        print(f"Access count for {url}: {access_count}")
        return func(*args, **kwargs)
    return wrapper


@track_access_count
@cache_with_expiry(expiration_seconds=10)
def get_page(url: str) -> str:
    response = requests.get(url)
    return response.text


if __name__ == "__main__":
    # Set up Redis client
    redis_client = redis.Redis()

    # Test the get_page function with tracking and caching
    slow_url = "http://slowwly.robertomurray.co.uk/delay/1000\
    /url/http://www.google.com"
    fast_url = "http://www.google.com"

    # This should take some time due to the simulated delay
    print(get_page(slow_url))
    print(get_page(fast_url))  # This should be faster as it is not delayed
    # This should be faster as it is retrieved from the cache
    print(get_page(slow_url))

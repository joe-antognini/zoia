"""Tools to interact with a Redis backend."""

import functools
import os

import redislite

from zoia.config import get_database_root


@functools.lru_cache(maxsize=1)
def get_redis_connection():
    """Return the connection object to the Redis server."""
    db_root = get_database_root()
    if db_root is None:
        raise RuntimeError('Library root is not defined.')

    db_filename = os.path.join(db_root, 'redis.db')
    serverconfig = {
        'save': '10 1',
        'appendonly': 'yes',
        'appendfsync': 'everysec',
        'appendfilename': 'redis.aof',
    }
    return redislite.Redis(os.path.join(db_filename, serverconfig))

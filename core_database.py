"""TinyDB kept in memory.

Each TinyDB operation used to reread and rewrite db.json. The cache serves
reads from memory and holds writes until flush_db(), which runs once per
request and again on process shutdown.
"""

import atexit

from tinydb import TinyDB
from tinydb.middlewares import CachingMiddleware
from tinydb.storages import JSONStorage


class _CachedJSONStorage(CachingMiddleware):
    # Do not flush after N writes. flush_db() is the only flush.
    WRITE_CACHE_SIZE = 2**31


db = TinyDB(
    "db.json",
    indent=2,
    encoding="utf-8",
    ensure_ascii=False,
    storage=_CachedJSONStorage(JSONStorage),
)


def get_db():
    return db


def flush_db() -> None:
    db.storage.flush()


atexit.register(flush_db)

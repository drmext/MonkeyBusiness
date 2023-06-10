import time
from os import stat
from shutil import copy

from tinydb import TinyDB
from tinydb.middlewares import CachingMiddleware
from tinydb.storages import JSONStorage

storage = CachingMiddleware(JSONStorage)
storage.WRITE_CACHE_SIZE = 5000

infile = "db.json"
outfile = f"db_{round(time.time())}.json"

copy(infile, outfile)

db = TinyDB(
    infile,
    indent=2,
    encoding="utf-8",
    ensure_ascii=False,
    storage=storage,
)

start_size = stat(infile).st_size

# Non-best tables for GITADORA and IIDX are not used in game
for table in ("guitarfreaks_scores", "drummania_scores", "iidx_scores"):
    db.drop_table(table)
    print("Dropped", table)

db.close()

end_size = stat(infile).st_size

print(f"{infile} {round((start_size - end_size) / 1024 / 1024, 2)} MiB trimmed")

import argparse
import time
from os import stat
from shutil import copy

from tinydb import TinyDB, where
from tinydb.middlewares import CachingMiddleware
from tinydb.storages import JSONStorage


def delete_scores(user_id, game):
    for scores in (f"{game}_scores_best", f"{game}_scores", f"{game}_profile"):
        if db.table(scores).search((where(f"{game}_id") == user_id)):
            db.table(scores).remove((where(f"{game}_id") == user_id))


# special case
def delete_gitadora_scores(user_id):
    for scores in (
        "guitarfreaks_scores_best",
        "drummania_scores_best",
        "guitarfreaks_scores",
        "drummania_scores",
        "gitadora_profile",
    ):
        if db.table(scores).search((where("gitadora_id") == user_id)):
            db.table(scores).remove((where("gitadora_id") == user_id))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-g", "--game", help="ex: ddr, gitadora, iidx", required=True)
    parser.add_argument("-i", "--user_id", help="ex: 12345678", required=True)
    args = parser.parse_args()

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

    game = args.game.lower()
    user_id = int(args.user_id.replace("-", ""))
    if game == "gitadora":
        delete_gitadora_scores(user_id)
    else:
        delete_scores(user_id, game)

    db.close()

    end_size = stat(infile).st_size

    print(f"{infile} {round((start_size - end_size) / 1024 / 1024, 2)} MiB trimmed")

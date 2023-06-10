import argparse
import xml.etree.ElementTree as ET

from tinydb import TinyDB, where
from tinydb.middlewares import CachingMiddleware
from tinydb.storages import JSONStorage


def main(automap_xml, version, monkey_db, ddr_id):
    storage = CachingMiddleware(JSONStorage)
    storage.WRITE_CACHE_SIZE = 5000

    db = TinyDB(
        monkey_db,
        indent=2,
        encoding="utf-8",
        ensure_ascii=False,
        storage=storage,
    )

    ddr_id = int(ddr_id.replace("-", ""))

    profile = db.table("ddr_profile").get(where("ddr_id") == ddr_id)
    if profile == None:
        raise SystemExit(f"ERROR: DDR profile {ddr_id} not in {monkey_db}")

    game_version = 19
    if profile["version"].get(str(game_version), None) == None:
        raise SystemExit(
            f"ERROR: DDR profile {ddr_id} version {game_version} not in {monkey_db}"
        )

    scores = []

    with open(automap_xml, "rb") as fp:
        automap_0 = fp.read().split(b"\n\n")

        if version == 19:
            playerdata = "playerdata"
        else:
            playerdata = "playerdata_2"

        scores_xml = False
        for xml in automap_0:
            tree = ET.ElementTree(ET.fromstring(xml.decode(encoding="shift-jis")))
            root = tree.getroot()
            if scores_xml:
                for music in root.findall(f"{playerdata}/music"):
                    mcode = int(music.find("mcode").text)
                    for difficulty, chart in enumerate(music.findall("note")):
                        if int(chart.find("count").text) > 0:
                            rank = int(chart.find("rank").text)
                            clearkind = int(chart.find("clearkind").text)
                            score = int(chart.find("score").text)
                            scores.append([mcode, difficulty, rank, clearkind, score])
                break
            else:
                try:
                    if root.find(f"{playerdata}/data/mode").text == "userload":
                        if len(root.find(f"{playerdata}/data/refid").text) == 16:
                            scores_xml = True
                except AttributeError:
                    continue

        total_count = len(scores)

        if total_count == 0:
            raise SystemExit("ERROR: No scores to import")

        for s in scores:
            mcode = s[0]
            difficulty = s[1]
            rank = s[2]
            lamp = s[3]
            score = s[4]
            exscore = 0

            print(
                f"mcode: {mcode}, difficulty: {difficulty}, rank: {rank}, score: {score}, lamp: {lamp}"
            )

            best = db.table("ddr_scores_best").get(
                (where("ddr_id") == ddr_id)
                & (where("game_version") == game_version)
                & (where("mcode") == mcode)
                & (where("difficulty") == difficulty)
            )
            best = {} if best is None else best

            best_score_data = {
                "game_version": game_version,
                "ddr_id": ddr_id,
                "playstyle": 0 if difficulty < 5 else 1,
                "mcode": mcode,
                "difficulty": difficulty,
                "rank": min(rank, best.get("rank", rank)),
                "lamp": max(lamp, best.get("lamp", lamp)),
                "score": max(score, best.get("score", score)),
                "exscore": max(exscore, best.get("exscore", exscore)),
            }

            ghostid = db.table("ddr_scores").get(
                (where("ddr_id") == ddr_id)
                & (where("game_version") == game_version)
                & (where("mcode") == mcode)
                & (where("difficulty") == difficulty)
                & (where("exscore") == best.get("exscore", exscore))
            )
            if ghostid:
                best_score_data["ghostid"] = ghostid.doc_id
            else:
                best_score_data["ghostid"] = -1

            db.table("ddr_scores_best").upsert(
                best_score_data,
                (where("ddr_id") == ddr_id)
                & (where("game_version") == game_version)
                & (where("mcode") == mcode)
                & (where("difficulty") == difficulty),
            )

    db.close()
    print()
    print(f"{total_count} scores imported to DDR profile {ddr_id} in {monkey_db}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--automap_xml", help="Input xml file", required=True)
    parser.add_argument(
        "--version",
        help="19 is A20P, 20 is A3",
        default=19,
        type=int,
    )
    parser.add_argument("--monkey_db", help="Output json file", required=True)
    parser.add_argument("--ddr_id", help="12345678", required=True)
    args = parser.parse_args()

    main(args.automap_xml, args.version, args.monkey_db, args.ddr_id)

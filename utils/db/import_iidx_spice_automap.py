import argparse
import xml.etree.ElementTree as ET
from enum import IntEnum

from tinydb import TinyDB, where
from tinydb.middlewares import CachingMiddleware
from tinydb.storages import JSONStorage


def main(automap_xml, version, monkey_db, iidx_id):
    class ClearFlags(IntEnum):
        NO_PLAY = 0
        FAILED = 1
        ASSIST_CLEAR = 2
        EASY_CLEAR = 3
        CLEAR = 4
        HARD_CLEAR = 5
        EX_HARD_CLEAR = 6
        FULL_COMBO = 7

    storage = CachingMiddleware(JSONStorage)
    storage.WRITE_CACHE_SIZE = 5000

    db = TinyDB(
        monkey_db,
        indent=2,
        encoding="utf-8",
        ensure_ascii=False,
        storage=storage,
    )

    iidx_id = int(iidx_id.replace("-", ""))

    profile = db.table("iidx_profile").get(where("iidx_id") == iidx_id)
    if profile == None:
        raise SystemExit(f"ERROR: IIDX profile {iidx_id} not in {monkey_db}")

    game_version = 30

    scores = []

    with open(automap_xml, "rb") as fp:
        automap_0 = fp.read().split(b"\n\n")

        scores_xml = False
        for xml in automap_0:
            try:
                tree = ET.ElementTree(ET.fromstring(xml.decode(encoding="shift-jis")))
                root = tree.getroot()
            except:
                continue
            if scores_xml:
                sp_dp = int(root.find(f"IIDX{version}music/style").get("type"))
                print(sp_dp)
                for m in root.findall(f"IIDX{version}music/m"):
                    score = [int(x) for x in m.text.split()]
                    if score[0] != -1:
                        # skip rivals
                        continue
                    music_id = score[1]
                    for difficulty in range(5):
                        d = difficulty + 2
                        if score[d] != -1:
                            clear_flg = score[d]
                            ex_score = score[d + 5]
                            miss_count = score[d + 10]
                            scores.append(
                                [
                                    sp_dp,
                                    music_id,
                                    difficulty,
                                    clear_flg,
                                    ex_score,
                                    miss_count,
                                ]
                            )
                scores_xml = False
            else:
                try:
                    if root.find(f"IIDX{version}music").get("method") == "getrank":
                        scores_xml = True
                except AttributeError:
                    continue

        total_count = len(scores)

        if total_count == 0:
            raise SystemExit("ERROR: No scores to import")

        for s in scores:
            play_style = s[0]
            music_id = s[1]
            difficulty = s[2]
            clear_flg = s[3]
            ex_score = s[4]
            miss_count = s[5]

            print(
                f"music_id: {music_id}, sp_dp: {play_style}, difficulty: {difficulty}, clear_flg: {clear_flg}, ex_score: {ex_score}, miss_count: {miss_count}"
            )

            best_score = db.table("iidx_scores_best").get(
                (where("iidx_id") == iidx_id)
                & (where("play_style") == play_style)
                & (where("music_id") == music_id)
                & (where("chart_id") == difficulty)
            )
            best_score = {} if best_score is None else best_score

            if clear_flg < ClearFlags.EASY_CLEAR:
                miss_count = -1
            best_miss_count = best_score.get("miss_count", miss_count)
            if best_miss_count == -1:
                miss_count = max(miss_count, best_miss_count)
            elif clear_flg > ClearFlags.ASSIST_CLEAR:
                miss_count = min(miss_count, best_miss_count)
            else:
                miss_count = best_miss_count
            best_ex_score = best_score.get("ex_score", ex_score)
            best_score_data = {
                "game_version": game_version,
                "iidx_id": iidx_id,
                "pid": 13,
                "play_style": play_style,
                "music_id": music_id,
                "chart_id": difficulty,
                "miss_count": miss_count,
                "ex_score": max(ex_score, best_ex_score),
                "ghost": best_score.get(
                    "ghost",
                    "00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000",
                ),
                "ghost_gauge": best_score.get(
                    "ghost_gauge",
                    "4c0400000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000",
                ),
                "clear_flg": max(clear_flg, best_score.get("clear_flg", clear_flg)),
                "gauge_type": best_score.get("gauge_type", 4),
            }

            db.table("iidx_scores_best").upsert(
                best_score_data,
                (where("iidx_id") == iidx_id)
                & (where("play_style") == play_style)
                & (where("music_id") == music_id)
                & (where("chart_id") == difficulty),
            )

            score_stats = db.table("iidx_score_stats").get(
                (where("music_id") == music_id)
                & (where("play_style") == play_style)
                & (where("chart_id") == difficulty)
            )
            score_stats = {} if score_stats is None else score_stats

            score_stats["game_version"] = game_version
            score_stats["play_style"] = play_style
            score_stats["music_id"] = music_id
            score_stats["chart_id"] = difficulty
            score_stats["play_count"] = score_stats.get("play_count", 0) + 1
            score_stats["fc_count"] = score_stats.get("fc_count", 0) + (
                1 if clear_flg == ClearFlags.FULL_COMBO else 0
            )
            score_stats["clear_count"] = score_stats.get("clear_count", 0) + (
                1 if clear_flg >= ClearFlags.EASY_CLEAR else 0
            )
            score_stats["fc_rate"] = int(
                (score_stats["fc_count"] / score_stats["play_count"]) * 1000
            )
            score_stats["clear_rate"] = int(
                (score_stats["clear_count"] / score_stats["play_count"]) * 1000
            )

            db.table("iidx_score_stats").upsert(
                score_stats,
                (where("music_id") == music_id)
                & (where("play_style") == play_style)
                & (where("chart_id") == difficulty),
            )

    db.close()
    print()
    print(f"{total_count} scores imported to IIDX profile {iidx_id} in {monkey_db}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--automap_xml", help="Input xml file", required=True)
    parser.add_argument(
        "--version",
        help="",
        default=30,
        type=int,
    )
    parser.add_argument("--monkey_db", help="Output json file", required=True)
    parser.add_argument("--iidx_id", help="12345678", required=True)
    args = parser.parse_args()

    main(args.automap_xml, args.version, args.monkey_db, args.iidx_id)

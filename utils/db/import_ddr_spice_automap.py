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


    with open(automap_xml, "rb") as fp:
        automap_0 = fp.read().split(b"\n\n")

        if version == 3:
            playerdata = "playdata_3"
            game_version = 20
        elif version == 2:
            playerdata = "playerdata_2"
            game_version = 19
        elif version == 1:
            playerdata = "playerdata"
            game_version = 19

        scores = []
        scores_xml = False
        for xml in automap_0:
            try:
                tree = ET.ElementTree(ET.fromstring(xml.decode(encoding="shift-jis")))
                root = tree.getroot()
            except:
                continue
            if version in (1, 2):
                if scores_xml:
                    for music in root.findall(f"{playerdata}/music"):
                        mcode = int(music.find("mcode").text)
                        for difficulty, chart in enumerate(music.findall("note")):
                            c = chart.find("count")
                            if c == None:
                                continue
                            if int(c.text) > 0:
                                rank = int(chart.find("rank").text)
                                clearkind = int(chart.find("clearkind").text)
                                score = int(chart.find("score").text)
                                scores.append([mcode, difficulty, rank, clearkind, score, -1])
                    break
                else:
                    try:
                        if root.find(f"{playerdata}/data/mode").text == "userload":
                            if len(root.find(f"{playerdata}/data/refid").text) == 16:
                                scores_xml = True
                    except AttributeError:
                        continue
            elif version == 3:
                if scores_xml:
                    for music in root.findall(f"{playerdata}/score"):
                        mcode = int(music.find("mcode").text)
                        for x in music.findall("score_single") + music.findall("score_double"):
                            s = x.find("score_str").text.split(",")
                            s = [int(val) for val in s]
                            difficulty = s[0] + 4 if x.tag == "score_double" else s[0]
                            rank = s[2]
                            clearkind = s[3]
                            score = s[4]
                            # flare = s[6]
                            scores.append([mcode, difficulty, rank, clearkind, score])
                    break
                else:
                    try:
                        a = root.find(f"{playerdata}")
                        if "method" in a.attrib:
                            if a.attrib["method"] == "playerdata_load":
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
            # flare = s[5]
            exscore = 0

            print(
                f"mcode: {mcode}, difficulty: {difficulty}, rank: {rank}, score: {score}, lamp: {lamp}"
            )

            best = db.table("ddr_scores_best").get(
                (where("ddr_id") == ddr_id)
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
                # "flare_force": max(flare, best.get("flare_force", flare)),
            }

            ghostid = db.table("ddr_scores").get(
                (where("ddr_id") == ddr_id)
                & (where("mcode") == mcode)
                & (where("difficulty") == difficulty)
                & (where("score") == max(score, best.get("score", score)))
            )
            if ghostid:
                best_score_data["ghostid"] = ghostid.doc_id
            else:
                best_score_data["ghostid"] = -1

            db.table("ddr_scores_best").upsert(
                best_score_data,
                (where("ddr_id") == ddr_id)
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
        help="1=A20P, 2=A3, 3=WORLD (automap_xml source version, not destination)",
        default=3,
        type=int,
    )
    parser.add_argument("--monkey_db", help="Output json file", required=True)
    parser.add_argument("--ddr_id", help="12345678", required=True)
    args = parser.parse_args()

    main(args.automap_xml, args.version, args.monkey_db, args.ddr_id)

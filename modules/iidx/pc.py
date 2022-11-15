from tinydb import Query, where

import config
import random

from fastapi import APIRouter, Request, Response

from core_common import core_process_request, core_prepare_response, E
from core_database import get_db

router = APIRouter(prefix="/local", tags=["local"])
router.model_whitelist = ["LDJ", "KDZ", "JDZ"]


def get_profile(cid):
    return get_db().table("iidx_profile").get(where("card") == cid)


def get_profile_by_id(iidx_id):
    return get_db().table("iidx_profile").get(where("iidx_id") == iidx_id)


def get_game_profile(cid, game_version):
    profile = get_profile(cid)

    return profile["version"].get(str(game_version), None)


def get_id_from_profile(cid):
    profile = get_db().table("iidx_profile").get(where("card") == cid)

    djid = "%08d" % profile["iidx_id"]
    djid_split = "-".join([djid[:4], djid[4:]])

    return profile["iidx_id"], djid_split


def calculate_folder_mask(profile):
    return (
        profile.get("_show_category_grade", 0) << 0
        | (profile.get("_show_category_status", 0) << 1)
        | (profile.get("_show_category_difficulty", 0) << 2)
        | (profile.get("_show_category_alphabet", 0) << 3)
        | (profile.get("_show_category_rival_play", 0) << 4)
        | (profile.get("_show_category_rival_winlose", 0) << 6)
        | (profile.get("_show_rival_shop_info", 0) << 7)
        | (profile.get("_hide_play_count", 0) << 8)
        | (profile.get("_hide_rival_info", 0) << 9)
    )


@router.post("/{gameinfo}/pc/get")
async def pc_get(request: Request):
    request_info = await core_process_request(request)
    game_version = request_info["game_version"]

    cid = request_info["root"][0].attrib["rid"]
    profile = get_game_profile(cid, game_version)
    djid, djid_split = get_id_from_profile(cid)

    if game_version == 20:
        response = E.response(
            E.pc(
                E.pcdata(
                    dach=profile["dach"],
                    dp_opt=profile["dp_opt"],
                    dp_opt2=profile["dp_opt2"],
                    dpnum=profile["dpnum"],
                    gno=profile["gno"],
                    gpos=profile["gpos"],
                    help=profile["help"],
                    hispeed=profile["hispeed"],
                    id=djid,
                    idstr=djid_split,
                    judge=profile["judge"],
                    judgeAdj=profile["judgeAdj"],
                    liflen=profile["lift"],
                    mode=profile["mode"],
                    name=profile["djname"],
                    notes=profile["notes"],
                    opstyle=profile["opstyle"],
                    pase=profile["pase"],
                    pid=profile["region"],
                    pmode=profile["pmode"],
                    sach=profile["sach"],
                    sdhd=profile["sdhd"],
                    sdtype=profile["sdtype"],
                    sp_opt=profile["sp_opt"],
                    spnum=profile["spnum"],
                    timing=profile["timing"],
                ),
                E.qprodata(
                    [
                        profile["head"],
                        profile["hair"],
                        profile["face"],
                        profile["hand"],
                        profile["body"],
                    ],
                    __type="u32",
                    __size=5 * 4,
                ),
                E.skin(
                    [
                        0,
                        profile["turntable"],
                        profile["explosion"],
                        profile["bgm"],
                        calculate_folder_mask(profile),
                        profile["sudden"],
                        0,
                        profile["categoryvoice"],
                        profile["note"],
                        profile["fullcombo"],
                        profile["keybeam"],
                        profile["judgestring"],
                        -1,
                        profile["soundpreview"],
                    ],
                    __type="s16",
                ),
                E.rlist(),
                E.commonboss(baron=0, deller=profile["deller"], orb=0),
                E.secret(
                    E.flg1(profile.get("secret_flg1", [-1]), __type="s64"),
                    E.flg2(profile.get("secret_flg2", [-1]), __type="s64"),
                    E.flg3(profile.get("secret_flg3", [-1]), __type="s64"),
                ),
                E.join_shop(
                    join_cflg=1, join_id=10, join_name=config.arcade, joinflg=1
                ),
                E.grade(
                    *[E.g(x, __type="u8") for x in profile["grade_values"]],
                    dgid=profile["grade_double"],
                    sgid=profile["grade_single"],
                ),
                E.redboss(
                    crush=profile.get("redboss_crush", 0),
                    open=profile.get("redboss_open", 0),
                    progress=profile.get("redboss_progress", 0),
                ),
                E.blueboss(
                    column0=profile.get("blueboss_column0", 0),
                    column1=profile.get("blueboss_column1", 0),
                    first_flg=profile.get("blueboss_first_flg", 0),
                    gauge=profile.get("blueboss_gauge", 0),
                    general=profile.get("blueboss_general", 0),
                    item=profile.get("blueboss_item", 0),
                    item_flg=profile.get("blueboss_item_flg", 0),
                    level=profile.get("blueboss_level", 0),
                    row0=profile.get("blueboss_row0", 0),
                    row1=profile.get("blueboss_row1", 0),
                    sector=profile.get("blueboss_sector", 0),
                ),
                E.yellowboss(
                    E.p_attack(
                        profile.get("yellowboss_p_attack", [0] * 7), __type="s32"
                    ),
                    E.pbest_attack(
                        profile.get("yellowboss_pbest_attack", [0] * 7), __type="s32"
                    ),
                    E.defeat(profile.get("yellowboss_defeat", [0] * 7), __type="bool"),
                    E.shop_damage(
                        profile.get("yellowboss_shop_damage", [0] * 7), __type="s32"
                    ),
                    critical=profile.get("yellowboss_critical", 0),
                    destiny=profile.get("yellowboss_destiny", 0),
                    first_flg=profile.get("yellowboss_first_flg", 1),
                    heroic0=profile.get("yellowboss_heroic0", 0),
                    heroic1=profile.get("yellowboss_heroic1", 0),
                    join_num=profile.get("yellowboss_join_num", 0),
                    last_select=profile.get("yellowboss_last_select", 0),
                    level=profile.get("yellowboss_level", 1),
                    shop_message=profile.get("yellowboss_shop_message", ""),
                    special_move=profile.get("yellowboss_special_move", ""),
                ),
                E.link5(
                    anisakis=1,
                    bad=1,
                    beachside=1,
                    beautiful=1,
                    broken=1,
                    castle=1,
                    china=1,
                    cuvelia=1,
                    exusia=1,
                    fallen=1,
                    flip=1,
                    glass=1,
                    glassflg=1,
                    qpro=1,
                    qproflg=1,
                    quaver=1,
                    reflec_data=1,
                    reunion=1,
                    sakura=1,
                    sampling=1,
                    second=1,
                    summer=1,
                    survival=1,
                    thunder=1,
                    titans=1,
                    treasure=1,
                    turii=1,
                    waxing=1,
                    whydidyou=1,
                    wuv=1,
                ),
                E.cafe(
                    astraia=1,
                    bastie=1,
                    beachimp=1,
                    food=0,
                    holysnow=1,
                    is_first=0,
                    ledvsscu=1,
                    pastry=0,
                    rainbow=1,
                    service=0,
                    trueblue=1,
                ),
                E.tricolettepark(
                    attack_rate=0,
                    boss0_damage=0,
                    boss0_stun=0,
                    boss1_damage=0,
                    boss1_stun=0,
                    boss2_damage=0,
                    boss2_stun=0,
                    boss3_damage=0,
                    boss3_stun=0,
                    is_union=0,
                    magic_gauge=0,
                    open_music=-1,
                    party=0,
                ),
                E.weekly(
                    mid=-1,
                    wid=1,
                ),
                E.packinfo(
                    music_0=-1,
                    music_1=-1,
                    music_2=-1,
                    pack_id=1,
                ),
                E.visitor(anum=1, pnum=2, snum=1, vs_flg=1),
                E.gakuen(music_list=-1),
                E.achievements(
                    E.trophy(profile.get("achievements_trophy", [])[:10], __type="s64"),
                    last_weekly=profile.get("achievements_last_weekly", 0),
                    pack=profile.get("achievements_pack_id", 0),
                    pack_comp=profile.get("achievements_pack_comp", 0),
                    rival_crush=0,
                    visit_flg=profile.get("achievements_visit_flg", 0),
                    weekly_num=profile.get("achievements_weekly_num", 0),
                ),
                E.step(
                    E.stamp(profile.get("stepup_stamp", ""), __type="bin"),
                    E.help(profile.get("stepup_help", ""), __type="bin"),
                    dp_ach=profile.get("stepup_dp_ach", 0),
                    dp_hdpt=profile.get("stepup_dp_hdpt", 0),
                    dp_level=profile.get("stepup_dp_level", 0),
                    dp_mplay=profile.get("stepup_dp_mplay", 0),
                    dp_round=profile.get("stepup_dp_round", 0),
                    review=profile.get("stepup_review", 0),
                    sp_ach=profile.get("stepup_sp_ach", 0),
                    sp_hdpt=profile.get("stepup_sp_hdpt", 0),
                    sp_level=profile.get("stepup_sp_level", 0),
                    sp_mplay=profile.get("stepup_sp_mplay", 0),
                    sp_round=profile.get("stepup_sp_round", 0),
                ),
            )
        )
    elif game_version == 19:
        response = E.response(
            E.pc(
                E.pcdata(
                    dach=profile["dach"],
                    dp_opt=profile["dp_opt"],
                    dp_opt2=profile["dp_opt2"],
                    dpnum=profile["dpnum"],
                    gno=profile["gno"],
                    help=profile["help"],
                    id=djid,
                    idstr=djid_split,
                    liflen=profile["lift"],
                    mode=profile["mode"],
                    name=profile["djname"],
                    notes=profile["notes"],
                    pase=profile["pase"],
                    pid=profile["region"],
                    pmode=profile["pmode"],
                    sach=profile["sach"],
                    sdhd=profile["sdhd"],
                    sdtype=profile["sdtype"],
                    sflg0=-1,
                    sflg1=-1,
                    sp_opt=profile["sp_opt"],
                    spnum=profile["spnum"],
                    timing=profile["timing"],
                ),
                E.qprodata(
                    [
                        profile["head"],
                        profile["hair"],
                        profile["face"],
                        profile["hand"],
                        profile["body"],
                    ],
                    __type="u32",
                    __size=5 * 4,
                ),
                E.skin(
                    [
                        profile["frame"],
                        profile["turntable"],
                        profile["explosion"],
                        profile["bgm"],
                        calculate_folder_mask(profile),
                        profile["sudden"],
                        0,
                        profile["categoryvoice"],
                        profile["note"],
                        profile["fullcombo"],
                        profile["keybeam"],
                        profile["judgestring"],
                        0,
                        0,
                    ],
                    __type="s16",
                ),
                E.grade(
                    dgid=profile["grade_double"],
                    sgid=profile["grade_single"],
                ),
                E.ex(),
                E.ocrs(),
                E.step(
                    E.sp_cflg("", __type="bin"),
                    E.dp_cflg("", __type="bin"),
                    dp_ach=0,
                    dp_dif=0,
                    sp_ach=0,
                    sp_dif=0,
                ),
                E.lincle(comflg=1),
                E.reflec(br=1, sg=1, sr=1, ssc=1, tb=1, tf=1, wu=1),
                E.phase2(wonder=1, yellow=1),
                E.event(knee=1, lethe=0, resist=0, jknee=1, jlethe=0, jresist=0),
                E.phase4(
                    qpro=1,
                    glass=1,
                    treasure=1,
                    beautiful=1,
                    quaver=1,
                    castle=1,
                    flip=1,
                    titans=1,
                    exusia=1,
                    waxing=1,
                    sampling=1,
                    beachside=1,
                    cuvelia=1,
                    qproflg=1,
                    glassflg=1,
                    reunion=1,
                    bad=1,
                    turii=1,
                    anisakis=1,
                    second=1,
                    whydidyou=1,
                    china=1,
                    fallen=1,
                    broken=1,
                    summer=1,
                    sakura=1,
                    wuv=1,
                    survival=1,
                    thunder=1,
                ),
                E.shop(
                    E.item([3, 3, 3], __type="u8"),
                    spitem=1,
                ),
                E.rlist(),
            )
        )
    elif game_version == 18:
        response = E.response(
            E.pc(
                E.pcdata(
                    dach=profile["dach"],
                    dp_opt=profile["dp_opt"],
                    dp_opt2=profile["dp_opt2"],
                    dpnum=profile["dpnum"],
                    gno=profile["gno"],
                    id=djid,
                    idstr=djid_split,
                    liflen=profile["lift"],
                    mcomb=0,
                    mode=profile["mode"],
                    name=profile["djname"],
                    ncomb=0,
                    pid=profile["region"],
                    pmode=profile["pmode"],
                    sach=profile["sach"],
                    sdhd=profile["sdhd"],
                    sdtype=profile["sdtype"],
                    sflg0=-1,
                    sflg1=-1,
                    sp_opt=profile["sp_opt"],
                    spnum=profile["spnum"],
                    timing=profile["timing"],
                ),
                E.skin(
                    [
                        profile["frame"],
                        profile["turntable"],
                        profile["explosion"],
                        profile["bgm"],
                        calculate_folder_mask(profile),
                        profile["sudden"],
                        0,
                        0,
                        0,
                        0,
                        0,
                        0,
                    ],
                    __type="u16",
                ),
                E.grade(
                    dgid="-1",
                    sgid="-1",
                ),
                E.ex(),
                E.ocrs(),
                E.rlist(),
            )
        )

    response_body, response_headers = await core_prepare_response(request, response)
    return Response(content=response_body, headers=response_headers)


@router.post("/{gameinfo}/pc/common")
async def pc_common(request: Request):
    request_info = await core_process_request(request)
    game_version = request_info["game_version"]

    if game_version == 20:
        response = E.response(
            E.pc(
                E.mranking(
                    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                    __type="u16",
                ),
                E.ir(beat=2),
                E.boss(phase=0),
                E.red(phase=2),
                E.yellow(phase=4),
                E.limit(phase=25),
                E.cafe(open=1),
                E.yellow_correct(
                    *[
                        E.detail(
                            avg_shop=7,
                            critical=2,
                            max_condition=18,
                            max_member=20,
                            max_resist=1,
                            min_condition=10,
                            min_member=1,
                            min_resist=1,
                            rival=2,
                        )
                        for detail in range(6)
                    ],
                    E.detail(
                        avg_shop=7,
                        critical=2,
                        max_condition=144,
                        max_member=20,
                        max_resist=1,
                        min_condition=80,
                        min_member=1,
                        min_resist=1,
                        rival=2,
                    ),
                    avg_shop=7,
                ),
                expire=600,
            )
        )
    elif game_version == 19:
        response = E.response(
            E.pc(
                E.secret(
                    E.mid([1901, 1914, 1946, 1955, 1956, 1966], __type="u16"),
                    E.open([1, 1, 1, 1, 1, 1], __type="bool"),
                ),
                E.boss(phase=2),
                E.ir(beat=2),
                E.travel(flg=1),
                E.lincle(phase=4),
                E.monex(no=3),
                expire=600,
            )
        )
    elif game_version == 18:
        response = E.response(
            E.pc(
                E.cmd(
                    gmbl=1,
                    gmbla=1,
                    regl=1,
                    rndp=1,
                    hrnd=1,
                    alls=1,
                ),
                E.lg(lea=1),
                E.ir(beat=3),
                E.ev(pha=2),
                expire=600,
            )
        )

    response_body, response_headers = await core_prepare_response(request, response)
    return Response(content=response_body, headers=response_headers)


@router.post("/{gameinfo}/pc/save")
async def pc_save(request: Request):
    request_info = await core_process_request(request)
    game_version = request_info["game_version"]

    root = request_info["root"][0]

    xid = int(root.attrib["iidxid"])
    clt = int(root.attrib["cltype"])

    profile = get_profile_by_id(xid)
    game_profile = profile["version"].get(str(game_version), {})

    if clt == 0:
        game_profile["sach"] = root.attrib["achi"]
        game_profile["sp_opt"] = root.attrib["opt"]
    elif clt == 1:
        game_profile["dach"] = root.attrib["achi"]
        game_profile["dp_opt"] = root.attrib["opt"]
        game_profile["dp_opt2"] = root.attrib["opt2"]

    for k in [
        "gno",
        "gpos",
        "help",
        "hispeed",
        "judge",
        "judgeAdj",
        "lift",
        "mode",
        "notes",
        "opstyle",
        "pnum",
        "sdhd",
        "sdtype",
        "timing",
    ]:
        if k in root.attrib:
            game_profile[k] = root.attrib[k]

    secret = root.find("secret")
    if secret is not None:
        for k in ["flg1", "flg2", "flg3", "flg4"]:
            flg = secret.find(k)
            if flg is not None:
                game_profile["secret_" + k] = [int(x) for x in flg.text.split(" ")]

    step = root.find("step")
    if step is not None:
        for k in [
            "dp_level",
            "dp_mplay",
            "enemy_damage",
            "enemy_defeat_flg",
            "mission_clear_num",
            "progress",
            "sp_level",
            "sp_mplay",
            "tips_read_list",
            "total_point",
        ]:
            game_profile["stepup_" + k] = int(step.attrib[k])

        is_track_ticket = step.find("is_track_ticket")
        if is_track_ticket is not None:
            game_profile["stepup_is_track_ticket"] = int(is_track_ticket.text)

    achievements = root.find("achievements")
    if achievements is not None:
        for k in [
            "last_weekly",
            "pack_comp",
            "pack_flg",
            "pack_id",
            "play_pack",
            "visit_flg",
            "weekly_num",
        ]:
            game_profile["achievements_" + k] = int(achievements.attrib[k])

        trophy = achievements.find("trophy")
        if trophy is not None:
            game_profile["achievements_trophy"] = [
                int(x) for x in trophy.text.split(" ")
            ]

    grade = request_info["root"][0].find("grade")
    if grade is not None:
        grade_values = []
        for g in grade.findall("g"):
            grade_values.append([int(x) for x in g.text.split(" ")])

        profile["grade_single"] = int(grade.attrib["sgid"])
        profile["grade_double"] = int(grade.attrib["dgid"])
        profile["grade_values"] = grade_values

    deller_amount = game_profile.get("deller", 0)
    commonboss = root.find("commonboss")
    if commonboss is not None:
        deller_amount = int(commonboss.attrib["deller"])
    game_profile["deller"] = deller_amount

    game_profile["spnum"] = game_profile.get("spnum", 0) + (1 if clt == 0 else 0)
    game_profile["dpnum"] = game_profile.get("dpnum", 0) + (1 if clt == 1 else 0)

    profile["version"][str(game_version)] = game_profile

    get_db().table("iidx_profile").upsert(profile, where("iidx_id") == xid)

    response = E.response(E.pc(iidxid=xid, cltype=clt))

    response_body, response_headers = await core_prepare_response(request, response)
    return Response(content=response_body, headers=response_headers)


@router.post("/{gameinfo}/pc/visit")
async def pc_visit(request: Request):
    request_info = await core_process_request(request)

    response = E.response(
        E.pc(
            aflg=1,
            anum=1,
            pflg=1,
            pnum=1,
            sflg=1,
            snum=1,
        )
    )

    response_body, response_headers = await core_prepare_response(request, response)
    return Response(content=response_body, headers=response_headers)


@router.post("/{gameinfo}/pc/reg")
async def pc_reg(request: Request):
    request_info = await core_process_request(request)
    game_version = request_info["game_version"]

    cid = request_info["root"][0].attrib["cid"]
    name = request_info["root"][0].attrib["name"]
    pid = request_info["root"][0].attrib["pid"]

    db = get_db().table("iidx_profile")
    all_profiles_for_card = db.get(Query().card == cid)

    if all_profiles_for_card is None:
        all_profiles_for_card = {"card": cid, "version": {}}

    if "iidx_id" not in all_profiles_for_card:
        iidx_id = random.randint(10000000, 99999999)
        all_profiles_for_card["iidx_id"] = iidx_id

    if game_version == 20:
        all_profiles_for_card["version"][str(game_version)] = {
            "game_version": game_version,
            "djname": name,
            "region": int(pid),
            "head": 0,
            "hair": 0,
            "face": 0,
            "hand": 0,
            "body": 0,
            "turntable": 0,
            "explosion": 0,
            "bgm": 0,
            "folder_mask": 0,
            "sudden": 0,
            "categoryvoice": 0,
            "note": 0,
            "fullcombo": 0,
            "keybeam": 0,
            "judgestring": 0,
            "soundpreview": 0,
            "dach": 0,
            "dp_opt": 0,
            "dp_opt2": 0,
            "dpnum": 0,
            "gno": 0,
            "gpos": 0,
            "help": 0,
            "hispeed": 0,
            "judge": 0,
            "judgeAdj": 0,
            "lift": 0,
            "mode": 0,
            "notes": 0,
            "opstyle": 0,
            "pase": 0,
            "pmode": 0,
            "sach": 0,
            "sdhd": 50,
            "sdtype": 0,
            "sp_opt": 0,
            "spnum": 0,
            "timing": 0,
            "deller": 0,
            # Step up mode
            "stepup_stamp": "",
            "stepup_help": "",
            "stepup_dp_ach": 0,
            "stepup_dp_hdpt": 0,
            "stepup_dp_level": 0,
            "stepup_dp_mplay": 0,
            "stepup_dp_round": 0,
            "stepup_review": 0,
            "stepup_sp_ach": 0,
            "stepup_sp_hdpt": 0,
            "stepup_sp_level": 0,
            "stepup_sp_mplay": 0,
            "stepup_sp_round": 0,
            # Grades
            "grade_single": -1,
            "grade_double": -1,
            "grade_values": [],
            # Achievements
            "achievements_trophy": [0] * 80,
            "achievements_last_weekly": 0,
            "achievements_pack_comp": 0,
            "achievements_pack_flg": 0,
            "achievements_pack_id": 0,
            "achievements_play_pack": 0,
            "achievements_visit_flg": 0,
            "achievements_weekly_num": 0,
            # Web UI/Other options
            "_show_category_grade": 0,
            "_show_category_status": 1,
            "_show_category_difficulty": 1,
            "_show_category_alphabet": 1,
            "_show_category_rival_play": 0,
            "_show_category_rival_winlose": 0,
            "_show_rival_shop_info": 0,
            "_hide_play_count": 0,
            "_hide_rival_info": 1,
        }
    elif game_version == 19:
        all_profiles_for_card["version"][str(game_version)] = {
            "game_version": game_version,
            "djname": name,
            "region": int(pid),
            "head": 0,
            "hair": 0,
            "face": 0,
            "hand": 0,
            "body": 0,
            "frame": 0,
            "turntable": 0,
            "explosion": 0,
            "bgm": 0,
            "folder_mask": 0,
            "sudden": 0,
            "categoryvoice": 0,
            "note": 0,
            "fullcombo": 0,
            "keybeam": 0,
            "judgestring": 0,
            "dach": 0,
            "dp_opt": 0,
            "dp_opt2": 0,
            "dpnum": 0,
            "gno": 0,
            "help": 0,
            "lift": 0,
            "mode": 0,
            "notes": 0,
            "pase": 0,
            "pmode": 0,
            "sach": 0,
            "sdhd": 50,
            "sdtype": 0,
            "sp_opt": 0,
            "spnum": 0,
            "timing": 0,
            # Grades
            "grade_single": -1,
            "grade_double": -1,
            "grade_values": [],
            # Web UI/Other options
            "_show_category_grade": 0,
            "_show_category_status": 1,
            "_show_category_difficulty": 1,
            "_show_category_alphabet": 1,
            "_show_category_rival_play": 0,
            "_show_category_rival_winlose": 0,
            "_show_rival_shop_info": 0,
            "_hide_play_count": 0,
            "_hide_rival_info": 1,
        }
    elif game_version == 18:
        all_profiles_for_card["version"][str(game_version)] = {
            "game_version": game_version,
            "djname": name,
            "region": int(pid),
            "frame": 0,
            "turntable": 0,
            "explosion": 0,
            "bgm": 0,
            "folder_mask": 0,
            "sudden": 0,
            "dach": 0,
            "dp_opt": 0,
            "dp_opt2": 0,
            "dpnum": 0,
            "gno": 0,
            "lift": 0,
            "mode": 0,
            "pmode": 0,
            "sach": 0,
            "sdhd": 50,
            "sdtype": 0,
            "sp_opt": 0,
            "spnum": 0,
            "timing": 0,
            # Grades
            "grade_single": -1,
            "grade_double": -1,
            "grade_values": [],
            # Web UI/Other options
            "_show_category_grade": 0,
            "_show_category_status": 1,
            "_show_category_difficulty": 1,
            "_show_category_alphabet": 1,
            "_show_category_rival_play": 0,
            "_show_category_rival_winlose": 0,
            "_show_rival_shop_info": 0,
            "_hide_play_count": 0,
            "_hide_rival_info": 1,
        }
    db.upsert(all_profiles_for_card, where("card") == cid)

    card, card_split = get_id_from_profile(cid)

    response = E.response(E.pc(id=card, id_str=card_split))

    response_body, response_headers = await core_prepare_response(request, response)
    return Response(content=response_body, headers=response_headers)


@router.post("/{gameinfo}/pc/logout")
async def pc_logout(request: Request):
    request_info = await core_process_request(request)

    response = E.response(E.pc())

    response_body, response_headers = await core_prepare_response(request, response)
    return Response(content=response_body, headers=response_headers)

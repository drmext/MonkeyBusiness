import config

import random
import time

from lxml.builder import ElementMaker

from kbinxml import KBinXML

from utils.arc4 import EamuseARC4
from utils.lz77 import EamuseLZ77


def _add_val_as_str(elm, val):
    new_val = str(val)

    if elm is not None:
        elm.text = new_val

    else:
        return new_val


def _add_bool_as_str(elm, val):
    return _add_val_as_str(elm, 1 if val else 0)


def _add_list_as_str(elm, vals):
    new_val = " ".join([str(val) for val in vals])

    if elm is not None:
        elm.text = new_val
        elm.attrib["__count"] = str(len(vals))

    else:
        return new_val


E = ElementMaker(
    typemap={
        int: _add_val_as_str,
        bool: _add_bool_as_str,
        list: _add_list_as_str,
        float: _add_val_as_str,
    }
)


async def core_get_game_version_from_software_version(software_version):
    _, model, dest, spec, rev, ext = software_version
    ext = int(ext)

# beatmaniaIIDX
    if model == "LDJ":
        if ext >= 2024100900:
            return 32
        elif ext >= 2023101800:
            return 31
        elif ext >= 2022101700:
            return 30
        elif ext >= 2021101300:
            return 29
        # TODO: Consolidate IIDX modules to easily support versions 21-28 (probably never)
        elif ext >= 2020102800:
            return 28
        elif ext >= 2019101600:
            return 27
        elif ext >= 2018110700:
            return 26
        elif ext >= 2017122100:
            return 25
        elif ext >= 2016102400:
            return 24
        elif ext >= 2015111100:
            return 23
        elif ext >= 2014091700:
            return 22
        elif ext >= 2013100200:
            return 21
        elif ext >= 2012010100:
            return 20
    elif model == "KDZ":
        return 19
    elif model == "JDZ":
        return 18
# Expand IIDX REVISIONS TO IIDX14; TODO: Import Duel0213 plugin. (Expand to IIDX9 in the future)
    elif model == "JDJ":
        return 17
    elif model == "I00":
        return 16
    elif model == "HDD":
        return 15
    elif model == "GLD":
        return 14
    elif model == "FDD":
        return 13
    elif model == "ECO":
        return 12
    elif model == "E11":
        return 11
    elif model == "D01":
        return 10
    elif model == "C02":
        return 9

# GITADORA
    elif model == "M32":
        if ext >= 2024031300: # GALAXY WAVE
            return 10
        elif ext >= 2022121400: # Fuzz-up
            return 9
        elif ext >= 2021042100: # High Voltage
            return 8
        elif ext >= 2019100200: # NEX+AGE
            return 7
        elif ext >= 2018072700: # EXCHAIN GDHDV3
            return 6
        # TODO: Support versions 1-5 (never)
# Enable matixx based on CORE plugin GDHDV2
        elif ext >= 2017090600: # matixx
            return 5
        elif ext >= 2017011800: # RE-EVOLVE
            return 4
        elif ext >= 2015042100: # TRI-BOOST
            return 3
        elif ext >= 2014021400: # OverDrive
            return 2
        elif ext >= 2013012400: # GITADORA
            return 1

# jubeat
    elif model == "L44":
        elif ext >= 2021042100: # btAve.
            return 12
        elif ext >= 2019100200: # Ave.
            return 11
        elif ext >= 2018072700: # festo
            return 10
        # TODO: 
        elif ext >= 2017090600: # clan
            return 9
        elif ext >= 2017011800: # qubell
            return 8
        elif ext >= 2015042100: # prop
            return 7
        elif ext >= 2014021400: # saucer ff
            return 6
        elif ext >= 2013012400: # saucer
            return 5
    elif model == "K44": # copious and append
        return 4
    elif model == "J44": # knit and append
        return 3
    elif model == "I44": # ripples and append
        return 2
    elif model == "H44": # jubeat and append
        return 1

#################################################################################################################
#                                                                                                               #
#    MASSIVE TO-DO STUFF: GDXG and GDVX support; Cleanup code and hopefully finish this behemoth of a demon.    #
#                                                                                                               #
#################################################################################################################


# Set variables for gdxg and gfdm
gcde.gdxg.l3 = ["L32", "L33"]
gcde.gdxg.k3 = ["K32", "K33"]
gcde.gdxg.j3 = ["J32", "J33"]
# GDXG (GDHDV1/GDHD-XG3)
    elif model in gcde.gdxg.l3: # GFDM XG3
            return 93
    elif model in gcde.gdxg.k3: # GFDM XG2
            return 92
    elif model in gcde.gdxg.j3: # GFDM XG
            return 91

# GDVX
    elif model in gcde.gfdm.k3: # GFDM V8
            return 88
    elif model in gcde.gfdm.j3: # GFDM V7
            return 87
    elif model in gcde.gfdm.i3: # GFDM V6
            return 86

# DDR
    elif model == "MDX":
        if ext >= 2024061200:  # DDR WORLD 
            return 23
        if ext >= 2022022800:  # DDR A3
            return 22
        if ext >= 2019022600:  # DDR A20 PLUS
            return 21
        if ext >= 2019022600:  # DDR A20
            return 20
        if ext >= 2016032800:  # DDR A
            return 19
        if ext >= 2014050900:  # DDR 2014
            return 18
        if ext >= 2013031000:  # DDR 2013
            return 17
        if ext >= 2011110501:  # DDR X3
            return 16
        if ext >= 2010060700:  # DDR X2 presume
            return 15
        if ext >= 2008122400:  # DDR X presume
            return 14

    elif model == "KFC":
        # TODO: Fix newer than 2022 versions (never, I don't play this game)
# TODO: Add Booth - Volks Wagen support
        if ext >= 2023042500:  # SDVX EG SC
            return 9
        if ext >= 2022042500:  # SDVX EG S2
            return 8
        if ext >= 2021021700:  # SDVX EG S1
            return 7
        if ext >= 2019022801:  # SDVX VW
            return 6
        if ext >= 2016122100:  # SDVX HH
            return 5
        if ext >= 2015120400:  # SDVX GW S2
            return 4
        if ext >= 2014112000:  # SDVX GW S1
            return 3
        if ext >= 2013060500:  # SDVX II
            return 2
        if ext >= 2012011800:  # SDVX BOOTH
            return 1

    elif model == "REC":
        return 1

    # TODO: ???
    # elif model == "PAN": # Enable op3, op2, forte, and op1 support
    #     return 0

    else:
        return 0


async def core_process_request(request):
    cl = request.headers.get("Content-Length")
    data = await request.body()

    if not cl or not data:
        return {}

    if "X-Compress" in request.headers:
        request.compress = request.headers.get("X-Compress")
    else:
        request.compress = None

    if "X-Eamuse-Info" in request.headers:
        xeamuseinfo = request.headers.get("X-Eamuse-Info")
        key = bytes.fromhex(xeamuseinfo[2:].replace("-", ""))
        xml_dec = EamuseARC4(key).decrypt(data[: int(cl)])
        request.is_encrypted = True
    else:
        xml_dec = data[: int(cl)]
        request.is_encrypted = False

    if request.compress == "lz77":
        xml_dec = EamuseLZ77.decode(xml_dec)

    xml = KBinXML(xml_dec, convert_illegal_things=True)
    root = xml.xml_doc
    xml_text = xml.to_text()
    request.is_binxml = KBinXML.is_binary_xml(xml_dec)

    if config.verbose_log:
        print()
        print("\033[94mREQUEST\033[0m:")
        print(xml_text)

    model_parts = (root.attrib["model"], *root.attrib["model"].split(":"))
    module = root[0].tag
    method = root[0].attrib["method"] if "method" in root[0].attrib else None
    command = root[0].attrib["command"] if "command" in root[0].attrib else None
    game_version = await core_get_game_version_from_software_version(model_parts)

    return {
        "root": root,
        "text": xml_text,
        "module": module,
        "method": method,
        "command": command,
        "model": model_parts[1],
        "dest": model_parts[2],
        "spec": model_parts[3],
        "rev": model_parts[4],
        "ext": model_parts[5],
        "game_version": game_version,
    }


async def core_prepare_response(request, xml):
    binxml = KBinXML(xml)

    if request.is_binxml:
        xml_binary = binxml.to_binary()
    else:
        xml_binary = binxml.to_text().encode("utf-8")  # TODO: Proper encoding

    if config.verbose_log:
        print("\033[91mRESPONSE\033[0m:")
        print(binxml.to_text())

    response_headers = {"User-Agent": "EAMUSE.Httpac/1.0"}

    if request.is_encrypted:
        xeamuseinfo = "1-%08x-%04x" % (int(time.time()), random.randint(0x0000, 0xFFFF))
        response_headers["X-Eamuse-Info"] = xeamuseinfo
        key = bytes.fromhex(xeamuseinfo[2:].replace("-", ""))
        response = EamuseARC4(key).encrypt(xml_binary)
    else:
        response = bytes(xml_binary)

    request.compress = None
    # if request.compress == "lz77":
    #     response_headers["X-Compress"] = request.compress
    #     response = EamuseLZ77.encode(response)

    return response, response_headers

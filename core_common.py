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

    if model == "LDJ":
        if ext >= 2023101800:
            return 31
        elif ext in range(2022101700, 2023101700):
            return 30
        elif ext in range(2021101300, 2022101500):
            return 29
        elif ext in range(2020102800, 2021100601):
            return 28
        elif ext in range(2019101600, 2020102201):
            return 27
        elif ext in range(2018110700, 2019100701):
            return 26
        elif ext in range(2017122100, 2018103101):
            return 25
        elif ext in range(2016102400, 2017082801):
            return 24
        elif ext in range(2015111100, 2016102001):
            return 23
        elif ext in range(2014091700, 2015080501):
            return 22
        elif ext in range(2013100200, 2014071601):
            return 21
        elif ext in range(2012091900, 2013090901):
            return 20
    elif model == "KDZ":
        return 19
    elif model == "JDZ":
        return 18

    elif model == "M32":
        if ext >= 2022121400:
            return 9
        elif ext >= 2021042100:
            return 8
        elif ext >= 2019100200:
            return 7
        elif ext >= 2018072700:
            return 6
        elif ext >= 2017090600:
            return 5
        elif ext >= 2017011800:
            return 4
        elif ext in range(2015042100, 2016112302):
            return 3
        elif ext in range(2014021400, 2015032702):
            return 2
        elif ext in range(2013012400, 2014011601):
            return 1

    elif model == "MDX":
        if ext >= 2019022600:  # ???
            return 19

    elif model == "KFC":
        if ext >= 2020090402:  # ???
            return 6

    elif model == "REC":
        return 1

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

    xml = KBinXML(xml_dec)
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

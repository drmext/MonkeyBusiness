import config

import threading
import time

from fastapi import HTTPException
from lxml.builder import ElementMaker

from kbinxml import KBinXML

from utils.arc4 import EamuseARC4
from utils.lz77 import lz77_decode, lz77_encode

# Skip LZ77 for tiny bodies that always expand under AVS framing overhead.
LZ77_MIN_RAW_BYTES = 256


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


_AVS_DEFAULT_SEED = 0x41C64E6D
_avs_prng_lock = threading.Lock()
_avs_prng_state = [0, 0]
_avs_prng_ready = False


def _avs_xorshift(state):
    s0, s1 = state[0], state[1]
    t = (s0 ^ ((s0 << 10) & 0xFFFFFFFF)) & 0xFFFFFFFF
    t ^= t >> 13
    r = (t ^ s1 ^ (s1 >> 10)) & 0xFFFFFFFF
    state[0] = s1
    state[1] = r
    return r


def _avs_seed(seed=0):
    global _avs_prng_ready
    if seed == 0:
        seed = _AVS_DEFAULT_SEED
    mixer = [0, seed & 0xFFFFFFFF]
    _avs_prng_state[0] = _avs_xorshift(mixer)
    _avs_prng_state[1] = _avs_xorshift(mixer)
    _avs_xorshift(mixer)  # discarded, same as AVS
    _avs_prng_ready = True


def avs_prng_uint16():
    with _avs_prng_lock:
        if not _avs_prng_ready:
            _avs_seed(0)
        return _avs_xorshift(_avs_prng_state) & 0xFFFF


def _parse_eamuse_info(header):
    """Return (unix_bytes, prng_bytes) or raise HTTPException(400)."""
    parts = header.split("-")
    if len(parts) != 3 or parts[0] != "1":
        raise HTTPException(status_code=400, detail="malformed X-Eamuse-Info")
    unix_hex, prng_hex = parts[1], parts[2]
    if len(unix_hex) != 8 or len(prng_hex) != 4:
        raise HTTPException(status_code=400, detail="malformed X-Eamuse-Info")
    try:
        return bytes.fromhex(unix_hex), bytes.fromhex(prng_hex)
    except ValueError:
        raise HTTPException(status_code=400, detail="malformed X-Eamuse-Info") from None


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
        if ext >= 2025091700:
            return 33
        elif ext >= 2024100900:
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

    elif model == "M32":
        if ext >= 2024031300:
            return 10
        elif ext >= 2022121400:
            return 9
        elif ext >= 2021042100:
            return 8
        elif ext >= 2019100200:
            return 7
        elif ext >= 2018072700:
            return 6
        # TODO: Support versions 1-5 (never)
        elif ext >= 2017090600:
            return 5
        elif ext >= 2017011800:
            return 4
        elif ext >= 2015042100:
            return 3
        elif ext >= 2014021400:
            return 2
        elif ext >= 2013012400:
            return 1

    elif model == "MDX":
        if ext >= 2024061200 and ext not in (2024042069, 2025042069): # GF
            return 20
        if ext >= 2019022600:  # ???
            return 19

    elif model == "KFC":
        if ext >= 2020090402:  # ???
            return 6

    elif model == "REC":
        return 1

    # TODO: ???
    # elif model == "PAN":
    #     return 0

    else:
        return 0


async def core_process_request(request):
    cl = request.headers.get("Content-Length")
    data = await request.body()

    if not cl or not data:
        raise HTTPException(status_code=400)

    request.compress = request.headers.get("X-Compress", "none") # intentionally lowercase 'none' (NOT None)
    if request.compress not in ("none", "lz77"):
        raise HTTPException(status_code=400, detail="unsupported X-Compress value")

    if "X-Eamuse-Info" in request.headers:
        unix_bytes, prng_bytes = _parse_eamuse_info(request.headers.get("X-Eamuse-Info"))
        xml_dec = EamuseARC4(unix_bytes, prng_bytes).decrypt(data[: int(cl)])
        request.is_encrypted = True
    else:
        xml_dec = data[: int(cl)]
        request.is_encrypted = False

    if request.compress == "lz77":
        xml_dec = lz77_decode(xml_dec)

    xml = KBinXML(xml_dec, convert_illegal_things=True)
    root = xml.xml_doc
    request.is_binxml = KBinXML.is_binary_xml(xml_dec)

    xml_text = None
    if config.verbose_log:
        xml_text = xml.to_text()
        eamuse_info = (
            request.headers.get("X-Eamuse-Info") if request.is_encrypted else "none"
        )
        print()
        print("\033[94mREQUEST\033[0m:")
        print(f"X-Eamuse-Info: {eamuse_info}")
        print(f"X-Compress: {request.compress}")
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

    response_headers = {"User-Agent": "EAMUSE.Httpac/1.0"}

    if config.response_compression and request.compress == "lz77":
        if len(xml_binary) >= LZ77_MIN_RAW_BYTES:
            encoded = lz77_encode(xml_binary)
            if len(encoded) < len(xml_binary):
                response_headers["X-Compress"] = "lz77"
                response = encoded
            else:
                response_headers["X-Compress"] = "none"  # intentionally lowercase 'none' (NOT None)
                response = xml_binary
        else:
            response_headers["X-Compress"] = "none"  # intentionally lowercase 'none' (NOT None)
            response = xml_binary
    else:
        response_headers["X-Compress"] = "none" # intentionally lowercase 'none' (NOT None)
        response = xml_binary


    if request.is_encrypted:
        unix_time = int(time.time()) & 0xFFFFFFFF
        prng = avs_prng_uint16()
        response_headers["X-Eamuse-Info"] = f"1-{unix_time:08x}-{prng:04x}"
        response = EamuseARC4(unix_time.to_bytes(4), prng.to_bytes(2)).encrypt(response)
    else:
        response = bytes(response)

    if config.verbose_log:
        print("\033[91mRESPONSE\033[0m:")
        print(f"X-Eamuse-Info: {response_headers.get('X-Eamuse-Info', 'none')}")
        print(f"X-Compress: {response_headers['X-Compress']}")
        print(binxml.to_text())

    return response, response_headers

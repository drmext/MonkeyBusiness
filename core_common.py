import config

import re
import threading
import time
from functools import partial

from lxml.etree import Element, iselement, tostring

from kbinxml import KBinXML

from utils.arc4 import EamuseARC4
from utils.lz77 import lz77_decode, lz77_encode

# Skip LZ77 for tiny bodies that always expand under AVS framing overhead.
LZ77_MIN_RAW_BYTES = 256

# XML declaration charset aliases -> kbinxml / binary codec name (xrpc-go EncodingByName).
_ENCODING_ALIASES = {
    "UTF-8": "UTF-8",
    "UTF8": "UTF-8",
    "SHIFT_JIS": "cp932",
    "SHIFT-JIS": "cp932",
    "SJIS": "cp932",
    "CP932": "cp932",
    "EUC-JP": "EUC_JP",
    "EUC_JP": "EUC_JP",
    "EUCJP": "EUC_JP",
    "ISO-8859-1": "ISO-8859-1",
    "ISO_8859-1": "ISO-8859-1",
    "ASCII": "ASCII",
}

# kbinxml codec -> AVS XML declaration / lxml tostring encoding name.
_XML_DECL_NAMES = {
    "UTF-8": "UTF-8",
    "cp932": "SHIFT_JIS",
    "EUC_JP": "EUC-JP",
    "ISO-8859-1": "ISO-8859-1",
    "ASCII": "ASCII",
}

_XML_DECL_ENCODING_RE = re.compile(
    br"""encoding\s*=\s*["']([^"']+)["']""", re.IGNORECASE
)


class EamuseError(Exception):
    """Bad e-amuse request; caught by the bare ASGI app and turned into an HTTP status."""

    __slots__ = ("status_code", "detail")

    def __init__(self, status_code: int = 400, detail: str | bytes = ""):
        self.status_code = status_code
        self.detail = detail
        super().__init__(detail if detail else status_code)


def _normalize_xml_encoding(name: str | None) -> str:
    """Map a declaration / alias to a kbinxml codec name; default UTF-8."""
    if not name:
        return "UTF-8"
    return _ENCODING_ALIASES.get(name.upper().replace(" ", ""), "UTF-8")


def _xml_decl_name(codec: str) -> str:
    """AVS / lxml declaration name for a kbinxml codec."""
    return _XML_DECL_NAMES.get(codec, "UTF-8")


def _detect_text_xml_encoding(data: bytes) -> str:
    """Read charset from <?xml ... encoding=...?>; default UTF-8."""
    head = data[:200]
    m = _XML_DECL_ENCODING_RE.search(head)
    if not m:
        return "UTF-8"
    try:
        return _normalize_xml_encoding(m.group(1).decode("ascii", errors="ignore"))
    except Exception:
        return "UTF-8"


def _attr_str(val):
    """Convert a keyword argument to an XML attribute string."""
    t = type(val)
    if t is str:
        return val
    if t is bool:
        return "1" if val else "0"
    if t is int or t is float:
        return str(val)
    if t is list:
        return " ".join(str(v) for v in val)
    raise TypeError(f"bad attribute type: {t.__name__}({val!r})")


class _ElementFactory:
    """Drop-in replacement for lxml.builder.ElementMaker with our typemap.

    Supports ``E.tag(...)`` and ``E("tag", ...)``. Hot tags are cached on the
    instance after the first ``__getattr__`` so loops do not allocate a fresh
    ``partial`` on every access.
    """

    __slots__ = ("__dict__",)

    def __call__(self, tag, *children, **attrib):
        elem = Element(tag)
        if attrib:
            for k, v in attrib.items():
                elem.attrib[k] = _attr_str(v)

        for item in children:
            t = type(item)
            if t is str:
                try:
                    last = elem[-1]
                except IndexError:
                    elem.text = (elem.text or "") + item
                else:
                    last.tail = (last.tail or "") + item
            elif t is bool:
                elem.text = "1" if item else "0"
            elif t is int or t is float:
                elem.text = str(item)
            elif t is list:
                elem.text = " ".join(str(v) for v in item)
                elem.attrib["__count"] = str(len(item))
            elif iselement(item):
                elem.append(item)
            else:
                raise TypeError(f"bad argument type: {t.__name__}({item!r})")

        return elem

    def __getattr__(self, tag):
        if tag.startswith("_"):
            raise AttributeError(tag)
        fn = partial(self, tag)
        setattr(self, tag, fn)
        return fn


E = _ElementFactory()


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
    """Return (unix_bytes, prng_bytes) or raise EamuseError(400)."""
    parts = header.split("-")
    if len(parts) != 3 or parts[0] != "1":
        raise EamuseError(400, "malformed X-Eamuse-Info")
    unix_hex, prng_hex = parts[1], parts[2]
    if len(unix_hex) != 8 or len(prng_hex) != 4:
        raise EamuseError(400, "malformed X-Eamuse-Info")
    try:
        return bytes.fromhex(unix_hex), bytes.fromhex(prng_hex)
    except ValueError:
        raise EamuseError(400, "malformed X-Eamuse-Info") from None


# (min_ext, version) newest-first; first match with ext >= min_ext wins.
_LDJ_VERSIONS = (
    (2025091700, 33),
    (2024100900, 32),
    (2023101800, 31),
    (2022101700, 30),
    (2021101300, 29),
    # TODO: Consolidate IIDX modules to easily support versions 21-28 (probably never)
    (2020102800, 28),
    (2019101600, 27),
    (2018110700, 26),
    (2017122100, 25),
    (2016102400, 24),
    (2015111100, 23),
    (2014091700, 22),
    (2013100200, 21),
    (2012010100, 20),
)

_M32_VERSIONS = (
    (2024031300, 10),
    (2022121400, 9),
    (2021042100, 8),
    (2019100200, 7),
    (2018072700, 6),
    # TODO: Support versions 1-5 (never)
    (2017090600, 5),
    (2017011800, 4),
    (2015042100, 3),
    (2014021400, 2),
    (2013012400, 1),
)


def _version_from_thresholds(ext, thresholds):
    for min_ext, ver in thresholds:
        if ext >= min_ext:
            return ver
    return 0


def core_get_game_version_from_software_version(software_version):
    _, model, dest, spec, rev, ext = software_version
    ext = int(ext)

    if model == "LDJ":
        return _version_from_thresholds(ext, _LDJ_VERSIONS)
    if model == "KDZ":
        return 19
    if model == "JDZ":
        return 18
    if model == "M32":
        return _version_from_thresholds(ext, _M32_VERSIONS)
    if model == "MDX":
        if ext >= 2024061200 and ext not in (2024042069, 2025042069):  # GF
            return 20
        if ext >= 2019022600:  # ???
            return 19
        return 0
    if model == "KFC":
        if ext >= 2020090402:  # ???
            return 6
        return 0
    if model == "REC":
        return 1
    # TODO: ???
    # if model == "PAN":
    #     return 0
    return 0


async def core_process_request(request):
    cl = request.headers.get("Content-Length")
    data = await request.body()

    if not cl or not data:
        raise EamuseError(400)

    request.compress = request.headers.get("X-Compress", "none") # intentionally lowercase 'none' (NOT None)
    if request.compress not in ("none", "lz77"):
        raise EamuseError(400, "unsupported X-Compress value")

    if "X-Eamuse-Info" in request.headers:
        unix_bytes, prng_bytes = _parse_eamuse_info(request.headers.get("X-Eamuse-Info"))
        xml_dec = EamuseARC4(unix_bytes, prng_bytes).decrypt(data[: int(cl)])
        request.is_encrypted = True
    else:
        xml_dec = data[: int(cl)]
        request.is_encrypted = False

    if request.compress == "lz77":
        xml_dec = lz77_decode(xml_dec)

    # Signature byte distinguishes binary; KBinXML.__init__ peeks the same way once.
    request.is_binxml = bool(xml_dec) and xml_dec[0] == 0xA0
    xml = KBinXML(xml_dec, convert_illegal_things=True)
    root = xml.xml_doc
    if request.is_binxml:
        request.xml_encoding = _normalize_xml_encoding(xml.encoding)
    else:
        request.xml_encoding = _detect_text_xml_encoding(xml_dec)

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
        print(
            f"Encoding: {_xml_decl_name(request.xml_encoding)}"
            f" ({'binary' if request.is_binxml else 'text'})"
        )
        print(xml_text)

    model_parts = (root.attrib["model"], *root.attrib["model"].split(":"))
    module = root[0].tag
    method = root[0].attrib["method"] if "method" in root[0].attrib else None
    command = root[0].attrib["command"] if "command" in root[0].attrib else None
    game_version = core_get_game_version_from_software_version(model_parts)

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


def core_prepare_response(request, xml):
    enc = getattr(request, "xml_encoding", None) or "UTF-8"
    binxml = KBinXML(xml)

    if request.is_binxml:
        xml_binary = binxml.to_binary(encoding=enc)
    else:
        # Compact on the wire; verbose_log pretty-prints separately via to_text().
        xml_binary = tostring(
            binxml.xml_doc,
            encoding=_xml_decl_name(enc),
            xml_declaration=True,
            pretty_print=False,
        )

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
        print(
            f"Encoding: {_xml_decl_name(enc)}"
            f" ({'binary' if request.is_binxml else 'text'})"
        )
        print(binxml.to_text())

    return response, response_headers

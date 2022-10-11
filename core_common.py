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
        elm.attrib['__count'] = str(len(vals))

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

    if model == 'LDJ' and ext >= 2021101300:
        return 29
    elif model == 'JDZ' and ext == 2011071200:
        return 18
    elif model == 'KDZ' and ext == 2012090300:
        return 19
    elif model == 'LDJ' and ext == 2013090900:
        return 20
    elif model == 'MDX' and ext >= 2019022600:
        return 19
    elif model == 'KFC' and ext >= 2020090402:
        return 6
    else:
        return 0


async def core_process_request(request):
    cl = request.headers.get('Content-Length')
    data = await request.body()

    if not cl or not data:
        return {}

    if 'X-Compress' in request.headers:
        request.compress = request.headers.get('X-Compress')
    else:
        request.compress = None

    if 'X-Eamuse-Info' in request.headers:
        xeamuseinfo = request.headers.get('X-Eamuse-Info')
        key = bytes.fromhex(xeamuseinfo[2:].replace("-", ""))
        xml_dec = EamuseARC4(key).decrypt(data[:int(cl)])
        request.is_encrypted = True
    else:
        xml_dec = data[:int(cl)]
        request.is_encrypted = False

    if request.compress == "lz77":
        xml_dec = EamuseLZ77.decode(xml_dec)

    xml = KBinXML(xml_dec)
    root = xml.xml_doc
    xml_text = xml.to_text()
    request.is_binxml = KBinXML.is_binary_xml(xml_dec)

    if config.verbose_log:
        print("Request:")
        print(xml_text)

    model_parts = (root.attrib['model'], *root.attrib['model'].split(':'))
    module = root[0].tag
    method = root[0].attrib['method'] if 'method' in root[0].attrib else None
    command = root[0].attrib['command'] if 'command' in root[0].attrib else None
    game_version = await core_get_game_version_from_software_version(model_parts)

    return {
        'root': root,
        'text': xml_text,
        'module': module,
        'method': method,
        'command': command,

        'model': model_parts[1],
        'dest': model_parts[2],
        'spec': model_parts[3],
        'rev': model_parts[4],
        'ext': model_parts[5],
        'game_version': game_version,
    }


async def core_prepare_response(request, xml):
    binxml = KBinXML(xml)

    if request.is_binxml:
        xml_binary = binxml.to_binary()
    else:
        xml_binary = binxml.to_text().encode("utf-8")  # TODO: Proper encoding

    if config.verbose_log:
        print("Response:")
        print(binxml.to_text())

    response_headers = {"User-Agent": "EAMUSE.Httpac/1.0"}

    if request.is_encrypted:
        xeamuseinfo = "1-%08x-%04x" % (int(time.time()), random.randint(0x0000, 0xffff))
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

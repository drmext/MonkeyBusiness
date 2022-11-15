# https://bsnk.me/eamuse/

from Cryptodome.Cipher import DES3


KEY = bytes(i * 2 for i in b"?I'llB2c.YouXXXeMeHaYpy!")
IV = bytes(8)

valid_characters = "0123456789ABCDEFGHJKLMNPRSTUWXYZ"


def enc_des(uid):
    cipher = DES3.new(KEY, DES3.MODE_CBC, IV)
    return cipher.encrypt(uid)


def dec_des(uid):
    cipher = DES3.new(KEY, DES3.MODE_CBC, IV)
    return cipher.decrypt(uid)


def checksum(data):
    chk = sum(data[i] * (i % 3 + 1) for i in range(15))
    while chk > 31:
        chk = (chk >> 5) + (chk & 31)
    return chk


def pack_5(data):
    data = "".join(f"{i:05b}" for i in data)
    if len(data) % 8 != 0:
        data += "0" * (8 - (len(data) % 8))
    return bytes(int(data[i : i + 8], 2) for i in range(0, len(data), 8))


def unpack_5(data):
    data = "".join(f"{i:08b}" for i in data)
    if len(data) % 5 != 0:
        data += "0" * (5 - (len(data) % 5))
    return bytes(int(data[i : i + 5], 2) for i in range(0, len(data), 5))


def to_konami_id(uid):
    assert len(uid) == 16, "UID must be 16 bytes"

    if uid.upper().startswith("E004"):
        card_type = 1
    elif uid.upper().startswith("0"):
        card_type = 2
    else:
        raise ValueError("Invalid UID prefix")

    kid = bytes.fromhex(uid)
    assert len(kid) == 8, "ID must be 8 bytes"

    out = bytearray(unpack_5(enc_des(kid[::-1]))[:13]) + bytes(3)

    out[0] ^= card_type
    out[13] = 1
    for i in range(1, 14):
        out[i] ^= out[i - 1]
    out[14] = card_type
    out[15] = checksum(out)

    return "".join(valid_characters[i] for i in out)


def to_uid(konami_id):
    if konami_id[14] == "1":
        card_type = 1
    elif konami_id[14] == "2":
        card_type = 2
    else:
        raise ValueError("Invalid ID")

    assert len(konami_id) == 16, f"ID must be 16 characters"
    assert all(
        i in valid_characters for i in konami_id
    ), "ID contains invalid characters"
    card = [valid_characters.index(i) for i in konami_id]
    assert card[11] % 2 == card[12] % 2, "Parity check failed"
    assert card[13] == card[12] ^ 1, "Card invalid"
    assert card[15] == checksum(card), "Checksum failed"

    for i in range(13, 0, -1):
        card[i] ^= card[i - 1]

    card[0] ^= card_type

    card_id = dec_des(pack_5(card[:13])[:8])[::-1]
    card_id = card_id.hex().upper()

    if card_type == 1:
        assert card_id[:4] == "E004", "Invalid card type"
    elif card_type == 2:
        assert card_id[0] == "0", "Invalid card type"
    return card_id


if __name__ == "__main__":
    assert to_konami_id("0000000000000000") == "007TUT8XJNSSPN2P", "To KID failed"
    assert to_uid("007TUT8XJNSSPN2P") == "0000000000000000", "From KID failed"
    assert (
        to_uid(to_konami_id("000000100200F000")) == "000000100200F000"
    ), "Roundtrip failed"

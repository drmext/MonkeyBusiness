"""Okumura LZSS: 4096-byte ring, max match 18, binary-tree matcher."""

N = 4096
F = 18
THRESHOLD = 2
NIL = N


def lz77_encode(data: bytes) -> bytes:
    if not data:
        return b"\x00\x00\x00"

    text_buf = bytearray(N + F - 1)
    lson = [0] * (N + 1)
    rson = [0] * (N + 257)
    dad = [0] * (N + 1)
    match_position = 0
    match_length = 0

    def init_tree() -> None:
        for i in range(N + 1, N + 257):
            rson[i] = NIL
        for i in range(N):
            dad[i] = NIL

    def insert_node(r: int) -> None:
        nonlocal match_position, match_length
        cmp_ = 1
        key = r
        p = N + 1 + text_buf[key]
        rson[r] = NIL
        lson[r] = NIL
        match_length = 0
        while True:
            if cmp_ >= 0:
                if rson[p] != NIL:
                    p = rson[p]
                else:
                    rson[p] = r
                    dad[r] = p
                    return
            else:
                if lson[p] != NIL:
                    p = lson[p]
                else:
                    lson[p] = r
                    dad[r] = p
                    return
            i = 1
            while i < F:
                cmp_ = text_buf[key + i] - text_buf[p + i]
                if cmp_ != 0:
                    break
                i += 1
            if i > match_length:
                match_position = p
                match_length = i
                if match_length >= F:
                    break
        dad[r] = dad[p]
        lson[r] = lson[p]
        rson[r] = rson[p]
        dad[lson[p]] = r
        dad[rson[p]] = r
        if rson[dad[p]] == p:
            rson[dad[p]] = r
        else:
            lson[dad[p]] = r
        dad[p] = NIL

    def delete_node(p: int) -> None:
        if dad[p] == NIL:
            return
        if rson[p] == NIL:
            q = lson[p]
        elif lson[p] == NIL:
            q = rson[p]
        else:
            q = lson[p]
            if rson[q] != NIL:
                while rson[q] != NIL:
                    q = rson[q]
                rson[dad[q]] = lson[q]
                dad[lson[q]] = dad[q]
                lson[q] = lson[p]
                dad[lson[p]] = q
            rson[q] = rson[p]
            dad[rson[p]] = q
        dad[q] = dad[p]
        if rson[dad[p]] == p:
            rson[dad[p]] = q
        else:
            lson[dad[p]] = q
        dad[p] = NIL

    init_tree()

    code_buf = bytearray(17)
    code_buf[0] = 0
    code_buf_ptr = 1
    mask = 1
    out = bytearray()

    def flush_code_buf() -> None:
        nonlocal code_buf_ptr, mask
        out.extend(code_buf[:code_buf_ptr])
        code_buf[0] = 0
        code_buf_ptr = 1
        mask = 1

    def emit_literal(c: int) -> None:
        nonlocal code_buf_ptr, mask
        code_buf[0] |= mask
        code_buf[code_buf_ptr] = c
        code_buf_ptr += 1
        mask <<= 1
        if mask & 0xFF == 0:
            flush_code_buf()

    def emit_match(distance: int, length: int) -> None:
        nonlocal code_buf_ptr, mask
        token = ((distance & 0xFFF) << 4) | ((length - (THRESHOLD + 1)) & 0x0F)
        code_buf[code_buf_ptr] = (token >> 8) & 0xFF
        code_buf[code_buf_ptr + 1] = token & 0xFF
        code_buf_ptr += 2
        mask <<= 1
        if mask & 0xFF == 0:
            flush_code_buf()

    data_pos = 0
    s = 0
    r = N - F
    # text_buf already zero-filled

    length = 0
    while length < F and data_pos < len(data):
        text_buf[r + length] = data[data_pos]
        data_pos += 1
        length += 1

    for i in range(1, F + 1):
        insert_node(r - i)
    insert_node(r)

    while length > 0:
        if match_length > length:
            match_length = length
        if match_length <= THRESHOLD:
            match_length = 1
            emit_literal(text_buf[r])
        else:
            distance = (r - match_position) & (N - 1)
            emit_match(distance, match_length)

        last_match_length = match_length
        i = 0
        while i < last_match_length:
            if data_pos >= len(data):
                break
            delete_node(s)
            c = data[data_pos]
            data_pos += 1
            text_buf[s] = c
            if s < F - 1:
                text_buf[s + N] = c
            s = (s + 1) & (N - 1)
            r = (r + 1) & (N - 1)
            insert_node(r)
            i += 1

        while i < last_match_length:
            delete_node(s)
            s = (s + 1) & (N - 1)
            r = (r + 1) & (N - 1)
            length -= 1
            if length != 0:
                insert_node(r)
            i += 1

    # Terminator: match token 0x0000, then flush the partial block
    code_buf[code_buf_ptr] = 0
    code_buf[code_buf_ptr + 1] = 0
    code_buf_ptr += 2
    out.extend(code_buf[:code_buf_ptr])
    return bytes(out)


def lz77_decode(data: bytes) -> bytes:
    text_buf = bytearray(N)
    r = N - F
    out = bytearray()
    flags = 0
    cur = 0

    while cur < len(data):
        flags >>= 1
        if (flags & 0x100) == 0:
            if cur >= len(data):
                break
            flags = data[cur] | 0xFF00
            cur += 1
        if flags & 1:
            if cur >= len(data):
                break
            c = data[cur]
            cur += 1
            out.append(c)
            text_buf[r] = c
            r = (r + 1) & (N - 1)
        else:
            if cur + 1 >= len(data):
                break
            token = (data[cur] << 8) | data[cur + 1]
            cur += 2
            if token < 0x10:
                break
            distance = token >> 4
            length = (token & 0x0F) + (THRESHOLD + 1)
            pos = (r - distance) & (N - 1)
            for _ in range(length):
                c = text_buf[pos]
                out.append(c)
                text_buf[r] = c
                r = (r + 1) & (N - 1)
                pos = (pos + 1) & (N - 1)

    return bytes(out)

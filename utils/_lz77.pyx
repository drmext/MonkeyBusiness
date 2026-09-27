# cython: language_level=3, boundscheck=False, wraparound=False
"""Okumura LZSS AVS binary-tree matcher."""

from libc.stdlib cimport free, calloc
from libc.string cimport memcpy
from cpython.object cimport PyObject
from cpython.ref cimport Py_XDECREF


cdef extern from "Python.h":
    PyObject *PyBytes_FromStringAndSize(const char *v, Py_ssize_t size) except NULL
    char *PyBytes_AS_STRING(PyObject *o) nogil
    int _PyBytes_Resize(PyObject **string, Py_ssize_t newsize) except -1


cdef enum:
    N = 4096
    F = 18
    THRESHOLD = 2
    NIL = 4096

cdef enum:
    DEC_DONE = 0
    DEC_NEED_SPACE = 1
    DEC_TRUNCATED = 2


cdef struct DecodeState:
    const unsigned char *src
    Py_ssize_t src_len
    Py_ssize_t cur
    unsigned char *out
    Py_ssize_t out_cap
    Py_ssize_t out_len
    Py_ssize_t need
    int flags


cdef void init_tree(unsigned short *lson, unsigned short *rson, unsigned short *dad) noexcept nogil:
    cdef int i
    for i in range(N + 1, N + 257):
        rson[i] = NIL
    for i in range(N):
        dad[i] = NIL


cdef void insert_node(
    unsigned char *text_buf,
    unsigned short *lson,
    unsigned short *rson,
    unsigned short *dad,
    int r,
    int *match_position,
    int *match_length,
) noexcept nogil:
    cdef int cmp_ = 1
    cdef int key = r
    cdef int p = N + 1 + text_buf[key]
    cdef int i
    rson[r] = NIL
    lson[r] = NIL
    match_length[0] = 0
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
            cmp_ = <int>text_buf[key + i] - <int>text_buf[p + i]
            if cmp_ != 0:
                break
            i += 1
        if i > match_length[0]:
            match_position[0] = p
            match_length[0] = i
            if match_length[0] >= F:
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


cdef void delete_node(
    unsigned short *lson,
    unsigned short *rson,
    unsigned short *dad,
    int p,
) noexcept nogil:
    cdef int q
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


cdef inline Py_ssize_t encode_bound(Py_ssize_t data_len) noexcept nogil:
    # All-literal worst case: 9 bytes per 8 input bytes, plus flag byte and terminator.
    return data_len + (data_len + 7) // 8 + 3


cdef Py_ssize_t encode_core(
    const unsigned char *src,
    Py_ssize_t data_len,
    unsigned char *text_buf,
    unsigned short *lson,
    unsigned short *rson,
    unsigned short *dad,
    unsigned char *out,
    Py_ssize_t out_cap,
) noexcept nogil:
    """Returns bytes written, or -1 if out_cap was too small."""
    cdef unsigned char code_buf[17]
    cdef int match_position = 0
    cdef int match_length = 0
    cdef int code_buf_ptr = 1
    cdef int mask = 1
    cdef Py_ssize_t out_len = 0
    cdef Py_ssize_t data_pos = 0
    cdef int s = 0
    cdef int r = N - F
    cdef int length = 0
    cdef int last_match_length
    cdef int i
    cdef unsigned char c
    cdef int distance
    cdef int token

    init_tree(lson, rson, dad)
    code_buf[0] = 0

    while length < F and data_pos < data_len:
        text_buf[r + length] = src[data_pos]
        data_pos += 1
        length += 1

    for i in range(1, F + 1):
        insert_node(text_buf, lson, rson, dad, r - i, &match_position, &match_length)
    insert_node(text_buf, lson, rson, dad, r, &match_position, &match_length)

    while length > 0:
        if match_length > length:
            match_length = length
        if match_length <= THRESHOLD:
            match_length = 1
            code_buf[0] |= mask
            code_buf[code_buf_ptr] = text_buf[r]
            code_buf_ptr += 1
        else:
            distance = (r - match_position) & (N - 1)
            token = ((distance & 0xFFF) << 4) | ((match_length - (THRESHOLD + 1)) & 0x0F)
            code_buf[code_buf_ptr] = (token >> 8) & 0xFF
            code_buf[code_buf_ptr + 1] = token & 0xFF
            code_buf_ptr += 2
        mask <<= 1
        if (mask & 0xFF) == 0:
            if out_len + code_buf_ptr > out_cap:
                return -1
            memcpy(out + out_len, code_buf, code_buf_ptr)
            out_len += code_buf_ptr
            code_buf[0] = 0
            code_buf_ptr = 1
            mask = 1

        last_match_length = match_length
        i = 0
        while i < last_match_length:
            if data_pos >= data_len:
                break
            delete_node(lson, rson, dad, s)
            c = src[data_pos]
            data_pos += 1
            text_buf[s] = c
            if s < F - 1:
                text_buf[s + N] = c
            s = (s + 1) & (N - 1)
            r = (r + 1) & (N - 1)
            insert_node(text_buf, lson, rson, dad, r, &match_position, &match_length)
            i += 1

        while i < last_match_length:
            delete_node(lson, rson, dad, s)
            s = (s + 1) & (N - 1)
            r = (r + 1) & (N - 1)
            length -= 1
            if length != 0:
                insert_node(text_buf, lson, rson, dad, r, &match_position, &match_length)
            i += 1

    code_buf[code_buf_ptr] = 0
    code_buf[code_buf_ptr + 1] = 0
    code_buf_ptr += 2
    if out_len + code_buf_ptr > out_cap:
        return -1
    memcpy(out + out_len, code_buf, code_buf_ptr)
    out_len += code_buf_ptr
    return out_len


def lz77_encode(const unsigned char[::1] data not None):
    cdef Py_ssize_t data_len = data.shape[0]
    if data_len == 0:
        return b"\x00\x00\x00"

    cdef const unsigned char *src = &data[0]
    cdef Py_ssize_t out_cap = encode_bound(data_len)
    cdef Py_ssize_t out_len
    cdef unsigned char *out
    cdef PyObject *raw = NULL
    cdef object result

    cdef unsigned char *text_buf = <unsigned char *>calloc(N + F - 1, 1)
    cdef unsigned short *lson = <unsigned short *>calloc(N + 1, sizeof(unsigned short))
    cdef unsigned short *rson = <unsigned short *>calloc(N + 257, sizeof(unsigned short))
    cdef unsigned short *dad = <unsigned short *>calloc(N + 1, sizeof(unsigned short))
    try:
        if text_buf == NULL or lson == NULL or rson == NULL or dad == NULL:
            raise MemoryError()
        raw = PyBytes_FromStringAndSize(NULL, out_cap)
        out = <unsigned char *>PyBytes_AS_STRING(raw)
        with nogil:
            out_len = encode_core(src, data_len, text_buf, lson, rson, dad, out, out_cap)
        if out_len < 0:
            raise RuntimeError("lz77_encode: output bound exceeded")
        _PyBytes_Resize(&raw, out_len)
        result = <object>raw
    finally:
        Py_XDECREF(raw)
        free(text_buf)
        free(lson)
        free(rson)
        free(dad)

    return result


cdef int decode_core(DecodeState *st) noexcept nogil:
    """Resumable: returns DEC_NEED_SPACE (with st.need set) without consuming the pending token."""
    cdef const unsigned char *src = st.src
    cdef Py_ssize_t src_len = st.src_len
    cdef Py_ssize_t cur = st.cur
    cdef unsigned char *out = st.out
    cdef Py_ssize_t out_cap = st.out_cap
    cdef Py_ssize_t out_len = st.out_len
    cdef int flags = st.flags
    cdef int status
    cdef int token
    cdef Py_ssize_t distance
    cdef Py_ssize_t length
    cdef Py_ssize_t back
    cdef Py_ssize_t j

    while True:
        if (flags & 0x100) == 0:
            if cur >= src_len:
                status = DEC_TRUNCATED
                break
            flags = src[cur] | 0xFF00
            cur += 1
        if flags & 1:
            if cur >= src_len:
                status = DEC_TRUNCATED
                break
            if out_len >= out_cap:
                st.need = out_len + 1
                status = DEC_NEED_SPACE
                break
            out[out_len] = src[cur]
            out_len += 1
            cur += 1
        else:
            if cur + 1 >= src_len:
                status = DEC_TRUNCATED
                break
            token = (src[cur] << 8) | src[cur + 1]
            if token < 0x10:
                cur += 2
                status = DEC_DONE
                break
            distance = token >> 4
            length = (token & 0x0F) + (THRESHOLD + 1)
            if out_len + length > out_cap:
                st.need = out_len + length
                status = DEC_NEED_SPACE
                break
            cur += 2
            # The window starts zero-filled, so references before the start of output read 0.
            back = out_len - distance
            if back >= 0 and distance >= length:
                memcpy(out + out_len, out + back, length)
                out_len += length
            else:
                for j in range(length):
                    out[out_len] = out[back] if back >= 0 else 0
                    out_len += 1
                    back += 1
        flags >>= 1

    st.cur = cur
    st.out_len = out_len
    st.flags = flags
    return status


def lz77_decode(const unsigned char[::1] data not None, bint strict=True):
    """Decode an LZ77 stream.

    With strict=True (default), raises ValueError if the stream ends before the
    terminator token. strict=False returns whatever was decoded, like lz77_ref.
    """
    cdef DecodeState st
    cdef PyObject *raw = NULL
    cdef Py_ssize_t new_cap
    cdef int status
    cdef object result

    st.src_len = data.shape[0]
    st.src = &data[0] if st.src_len > 0 else NULL
    st.cur = 0
    st.out_len = 0
    st.need = 0
    st.flags = 0
    st.out_cap = st.src_len * 4 + 64
    if st.out_cap < 256:
        st.out_cap = 256

    try:
        raw = PyBytes_FromStringAndSize(NULL, st.out_cap)
        st.out = <unsigned char *>PyBytes_AS_STRING(raw)
        while True:
            with nogil:
                status = decode_core(&st)
            if status != DEC_NEED_SPACE:
                break
            new_cap = st.out_cap * 2
            if new_cap < st.need:
                new_cap = st.need
            _PyBytes_Resize(&raw, new_cap)
            st.out = <unsigned char *>PyBytes_AS_STRING(raw)
            st.out_cap = new_cap
        if status == DEC_TRUNCATED and strict:
            raise ValueError(
                f"truncated lz77 stream: no terminator after {st.cur} input bytes "
                f"({st.out_len} bytes decoded)"
            )
        _PyBytes_Resize(&raw, st.out_len)
        result = <object>raw
    finally:
        Py_XDECREF(raw)

    return result

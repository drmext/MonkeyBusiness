import config

__all__ = ["lz77_encode", "lz77_decode"]

try:
    if __package__:
        from ._lz77 import lz77_decode, lz77_encode
    else:
        from _lz77 import lz77_decode, lz77_encode
except ImportError:
    if __package__:
        from .lz77_ref import lz77_decode, lz77_encode
    else:
        from lz77_ref import lz77_decode, lz77_encode
    if config.response_compression:
        print("cython lz77 extension is not built; using SLOW python lz77_ref.")


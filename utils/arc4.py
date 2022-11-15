from Cryptodome.Cipher import ARC4
from Cryptodome.Hash import MD5


class EamuseARC4:
    def __init__(self, eamuseKey):
        self.internal_key = bytearray.fromhex(
            "69D74627D985EE2187161570D08D93B12455035B6DF0D8205DF5"
        )
        self.key = MD5.new(eamuseKey + self.internal_key).digest()

    def decrypt(self, data):
        return ARC4.new(self.key).decrypt(bytes(data))

    def encrypt(self, data):
        return ARC4.new(self.key).encrypt(bytes(data))

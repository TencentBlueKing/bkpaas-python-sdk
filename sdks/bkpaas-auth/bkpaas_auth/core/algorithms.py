# -*- coding: utf-8 -*-
from collections.abc import Iterator


class ARC4:
    """ARC4 算法的实现

    注意：ARC4 加密算法很容易被破解，目前项目中仅用于解编码（类似 base64 的作用）
    """

    def __init__(self, key: bytes | bytearray) -> None:
        assert isinstance(key, (bytes, bytearray))

        s = list(range(0x100))
        j = 0
        for i in range(0x100):
            j = (s[i] + key[i % len(key)] + j) & 0xFF
            s[i], s[j] = s[j], s[i]

        self.s = s
        self.key_stream = self._key_stream_generator()

    def encrypt(self, data: bytes | bytearray) -> bytes:
        """加密数据"""
        return self._crypt(data)

    def decrypt(self, data: bytes | bytearray) -> bytes:
        """解密数据"""
        return self._crypt(data)

    def _crypt(self, data: bytes | bytearray) -> bytes:
        assert isinstance(data, (bytes, bytearray))
        return bytes([a ^ b for a, b in zip(data, self.key_stream)])

    def _key_stream_generator(self) -> Iterator[int]:
        s = self.s.copy()
        x = y = 0
        while True:
            x = (x + 1) & 0xFF
            y = (s[x] + y) & 0xFF
            s[x], s[y] = s[y], s[x]
            i = (s[x] + s[y]) & 0xFF
            yield s[i]

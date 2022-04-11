# -*- coding: utf-8 -*-
from enum import IntEnum


class ProviderType(IntEnum):
    UIN = 1
    RTX = 2
    BK = 3
    DATABASE = 9

    def get_id_prefix(self):
        return '{0:02d}'.format(self.value)

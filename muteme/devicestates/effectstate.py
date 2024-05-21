from enum import IntEnum


class EffectState(IntEnum):
    OFF       = 0x00
    DIM       = 0x10
    FASTPULSE = 0x20
    SLOWPULSE = 0x30
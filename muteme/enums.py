from enum import IntEnum


class LightState(IntEnum):
    OFF       = 0x00
    RED       = 0x01
    GREEN     = 0x02
    YELLOW    = 0x03
    BLUE      = 0x04
    PURPLE    = 0x05
    CYAN      = 0x06
    WHITE     = 0x07
    DIM       = 0x10
    FASTPULSE = 0x20
    SLOWPULSE = 0x30


class DeviceState(IntEnum):
    # Data sent from MuteMe
    START_TOUCH = 0x04
    TOUCHING    = 0x01
    END_TOUCH   = 0x02
    CLEAR       = 0x00
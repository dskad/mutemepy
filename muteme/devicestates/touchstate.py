from enum import IntEnum


class TouchState(IntEnum):
    # Data sent from MuteMe
    START_TOUCH = 0x04
    TOUCHING    = 0x01
    END_TOUCH   = 0x02
    CLEAR       = 0x00
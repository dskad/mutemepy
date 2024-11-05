import logging
import sys

from mutemepy import MuteMe
from mutemepy.devicestates import ColorState, EffectState

log = logging.getLogger()
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s %(levelname)s [%(name)s:%(lineno)d] %(message)s",
)


def toggle_color(count) -> None:
    if myMuteMe.color == ColorState.GREEN:
        myMuteMe.color = ColorState.RED
    else:
        myMuteMe.color = ColorState.GREEN


def toggle_pulse(count) -> None:
    if myMuteMe.effect == EffectState.FASTPULSE:
        myMuteMe.effect = EffectState.OFF
    else:
        myMuteMe.effect = EffectState.FASTPULSE
    log.debug(f"Multi-tap count: {count}")
    if count == 4:
        sys.exit(0)


myMuteMe = MuteMe()
myMuteMe.color = ColorState.GREEN
myMuteMe.on_tap(toggle_color)
myMuteMe.on_long_tap_start(toggle_color)
myMuteMe.on_long_tap_end(toggle_color)
myMuteMe.on_multi_tap(toggle_pulse)

try:
    myMuteMe.connect()

except KeyboardInterrupt:
    pass

except Exception as error:
    log.critical(error)

finally:
    log.warning("Shutting down...")
    myMuteMe.close()

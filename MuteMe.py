import asyncio
import logging
from muteme import MuteMe
from muteme.devicestates import ColorState, EffectState

log = logging.getLogger()
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s %(levelname)s [%(name)s:%(lineno)d] %(message)s",
)


def toggle_color() -> None:
    if myMuteMe.color == ColorState.GREEN:
        myMuteMe.color = ColorState.RED
    else:
        myMuteMe.color = ColorState.GREEN


def toggle_pulse() -> None:
    if myMuteMe.effect == EffectState.FASTPULSE:
        myMuteMe.effect = EffectState.OFF
    else:
        myMuteMe.effect = EffectState.FASTPULSE


myMuteMe = MuteMe()
myMuteMe.color = ColorState.GREEN
myMuteMe.on_tap(toggle_color)
myMuteMe.on_long_tap_start(toggle_color)
myMuteMe.on_long_tap_end(toggle_color)
myMuteMe.on_multi_tap(toggle_pulse)


# TODO: Can this move into the class so the user doesn't need to worry about async code?
async def main():
    async with asyncio.TaskGroup() as task_group:
        task_group.create_task(myMuteMe.connect())


try:
    asyncio.run(main(), debug=False)

except KeyboardInterrupt:
    pass

except Exception as error:
    log.critical(error)

finally:
    log.warning("Shutting down...")
    myMuteMe.close()

import asyncio
import logging
from muteme.muteme import MuteMe
from muteme.enums import LightState

log = logging.getLogger()
logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s %(levelname)s [%(name)s:%(lineno)d] %(message)s"
)

VID = 0x20A0
PID = 0x42DA

# TODO: on_tap resets blink, need to determine if currently blinking. 
#       Maybe light state needs to be a bitmap so light state changes don't walk on each other.
def on_tap(button) -> None:
    if button.light_state == LightState.GREEN:
        button.light_state = LightState.RED
    else:
        button.light_state = LightState.GREEN


def on_long_tap(button) -> None:
    if button.light_state == LightState.GREEN:
        button.light_state = LightState.RED
    else:
        button.light_state = LightState.GREEN


def on_double_tap(button: MuteMe) -> None:
    log.debug(f"Before XOR: {button.light_state}")
    button.light_state = button.light_state ^ LightState.FASTPULSE
    log.debug(f"After XOR: {button.light_state}")


myMuteMe = MuteMe(VID, PID)
myMuteMe.light_state = LightState.GREEN
myMuteMe.on_tap(on_tap)
myMuteMe.on_long_tap_start(on_long_tap)
myMuteMe.on_long_tap_end(on_long_tap)
myMuteMe.on_double_tap(on_double_tap)


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

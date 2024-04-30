import asyncio
import logging
from muteme.muteme import MuteMe
from muteme.enums import LightState

log = logging.getLogger()
logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s %(levelname)s [%(name)s:%(lineno)d] %(message)s"
)

# TODO: on_tap resets blink, need to determine if currently blinking. 
#       Maybe light state needs to be a bitmap so light state changes don't walk on each other.
def on_tap(button) -> None:
    if myMuteMe.light_state == LightState.GREEN:
        myMuteMe.light_state = LightState.RED
    else:
        myMuteMe.light_state = LightState.GREEN


def on_long_tap(button) -> None:
    if myMuteMe.light_state == LightState.GREEN:
        myMuteMe.light_state = LightState.RED
    else:
        myMuteMe.light_state = LightState.GREEN


def on_double_tap(button) -> None:
    log.debug(f"Before XOR: {myMuteMe.light_state}")
    current_light_state: int = myMuteMe.light_state
    myMuteMe.light_state = current_light_state ^ LightState.FASTPULSE
    log.debug(f"After XOR: {myMuteMe.light_state}")


myMuteMe = MuteMe()
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

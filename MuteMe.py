import asyncio
import logging
from muteme.muteme import MuteMe
from muteme.enums import LightState 

log = logging.getLogger()
logging.basicConfig(level=logging.DEBUG,
                     format="%(asctime)s %(levelname)s [%(name)s] %(message)s"
                     )

VID = 0x20A0
PID = 0x42DA

def on_tap(button) -> None:
    if button.lightState == LightState.GREEN:
        button.lightState =LightState.RED
    else:
        button.lightState = LightState.GREEN
        
def on_long_tap(button) -> None:
    if button.lightState == LightState.GREEN:
        button.lightState =LightState.RED
    else:
        button.lightState = LightState.GREEN

def on_double_tap(button: MuteMe) -> None:
    log.debug(f"Before XOR: {button.lightState}")
    button.lightState = button.lightState ^ LightState.FASTPULSE
    log.debug(f"After XOR: {button.lightState}")
    
myMuteMe = MuteMe(VID,PID)
myMuteMe.lightState = LightState.GREEN
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
        


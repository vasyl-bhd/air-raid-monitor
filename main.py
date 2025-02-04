import json
import logging
import time
from urllib.error import HTTPError, URLError
from urllib.request import urlopen

from air_raid.aid_raid_screen import AirRaidScreen
from epd.eink import Eink
from observer import Observable

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


def get_state():
    with urlopen('https://sirens.in.ua/api/v1/', timeout=10) as response:
        data = response.read()
        return json.loads(data)
    return None


def main():
    observable = Observable()
    e_ink = Eink()
    AirRaidScreen(observable, e_ink)
    try:
        main_cycle(observable)
    except IOError as e:
        print("IOError: " + str(e))
    except KeyboardInterrupt:
        logging.info("Interrupting keyboard")
        e_ink.close()
        exit()


def main_cycle(observable):
    curr_state = {}
    prev_state = {}
    timeout_count = 0
    while True:
        try:
            curr_state = get_state()
            timeout_count = 0
        except (HTTPError, URLError, IOError) as e:
            print("Error: " + str(e))
            timeout_count += 1
        finally:
            if timeout_count >= 3:
                curr_state = None
            if curr_state != prev_state:
                prev_state = curr_state
                observable.update_observers(curr_state)
            time.sleep(10)


if __name__ == "__main__":
    main()

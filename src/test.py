from modules.monitors import Monitors
import logging
import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--debug", action="store_true")
    args = parser.parse_args()

    logging.basicConfig(level=logging.DEBUG if args.debug else logging.INFO, format='[%(filename)s] [%(name)s] [%(funcName)s] [%(levelname)s] %(message)s')

    monitors = Monitors()
    for x in monitors.monitors:
        print(x.name, x.width, x.height)
    
    monitors.monitors[0].width = 1360
    monitors.save()
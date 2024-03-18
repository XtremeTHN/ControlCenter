from modules.displays import Displays
import logging
import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--debug", action="store_true")
    args = parser.parse_args()

    logging.basicConfig(level=logging.DEBUG if args.debug else logging.INFO, format='[%(filename)s] [%(name)s] [%(funcName)s] [%(levelname)s] %(message)s')

    Displays()
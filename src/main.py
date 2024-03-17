from modules.application import ControlCenter
import logging
import argparse

APP_ID="com.github.XtremeTHN.ControlCenter"

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--debug", action="store_true")
    args = parser.parse_args()

    logging.basicConfig(level=logging.DEBUG if args.debug else logging.INFO, format='[%(filename)s] [%(name)s] [%(funcName)s] [%(levelname)s] %(message)s')

    ControlCenter().run()
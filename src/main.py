from modules.application import ControlCenter
import logging

APP_ID="com.github.XtremeTHN.ControlCenter"

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG, format='[%(filename)s] [%(name)s] [%(funcName)s] [%(levelname)s] %(message)s')

    logging.info('Hello world!')
    ControlCenter().run()
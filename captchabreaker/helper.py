import os

import logging
from captchabreaker import config
from logging.handlers import RotatingFileHandler


def get_app_base_path():
    return os.path.dirname(os.path.realpath(__file__))


def get_instance_folder_path():
    return os.path.join(get_app_base_path(), 'instance')


def set_file_logger(app):
    handler = RotatingFileHandler(config.LOG_FILENAME, maxBytes=1e6, backupCount=10)
    handler.setLevel(logging.DEBUG)
    app.logger.addHandler(handler)
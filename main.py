from typing import Any
import logging
import pika
import toml
import os
import celery

confHandler: dict[str, Any]
mqHandler: pika.BlockingConnection
logger: logging.Logger
celeryHandler: celery.Celery


def initConf():
    try:
        confHandler = toml.load(
            os.path.join(os.path.abspath(os.path.dirname(__file__)), "conf.toml")
        )
        return confHandler
    except FileNotFoundError:
        logger.error("[Main>initConf] config toml file not found.")
        return None


def initLogger(
    level: int = logging.INFO,
    enable_terminal_log: bool = True,
    enable_log_file: bool = False,
    logFileName: str = "exec.log",
):
    main_log_handler = logging.getLogger(__name__)
    main_log_handler.setLevel(logging.INFO if level is None else level)
    log_formatter = logging.Formatter(
        "%(asctime)s - %(filename)s[line:%(lineno)d][%(levelname)s] %(message)s"
    )
    if enable_terminal_log:
        log_stream_handler = logging.StreamHandler()
        log_stream_handler.setFormatter(log_formatter)
        main_log_handler.addHandler(log_stream_handler)
    if enable_log_file:
        log_file_handler = logging.FileHandler(logFileName, mode="a")
        log_file_handler.setFormatter(log_formatter)
        main_log_handler.addHandler(log_file_handler)
    return main_log_handler


def initHandlers():
    logger.info("Init config handler.")
    confHandler = initConf()
    mqConnConf: pika.ConnectionParameters
    if confHandler is None:
        logger.error("[Main>init] initConf faild.")
        return False, {}, pika.BlockingConnection()
    logger.info("Init message queue handler.")
    if confHandler["rabbitmq"]["user"] != "" and confHandler["rabbitmq"]["pass"] != "":
        logger.info("Init message queue auth handler.")
        mqAuth = pika.PlainCredentials(
            username=confHandler["rabbitmq"]["user"],
            password=confHandler["rabbitmq"]["pass"],
        )
        mqConnConf: pika.ConnectionParameters = pika.ConnectionParameters(
            host=confHandler["rabbitmq"]["addr"],
            port=confHandler["rabbitmq"]["port"],
            credentials=mqAuth,
        )
    else:
        mqConnConf: pika.ConnectionParameters = pika.ConnectionParameters(
            host=confHandler["rabbitmq"]["addr"], port=confHandler["rabbitmq"]["port"]
        )
    mqHandler = pika.BlockingConnection(mqConnConf)
    return True, confHandler, mqHandler


def init():
    global logger, confHandler, mqHandler
    logger = initLogger()
    (initStatus, confHandler, mqHandler) = initHandlers()

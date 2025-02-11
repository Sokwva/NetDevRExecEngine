import celery
import os
import logging
from main import initConf, initLogger
from devExec.common import InputStruct
from devExec.baseLib import DevExec, TypeForkExec
from devExec.formater import Formater
from extendDrv.TFE.tfe import TFEDevFuncMap

confHandler = initConf()
logger = initLogger(
    logging.INFO
    if confHandler is None or confHandler["common"]["logLevel"] is None
    else confHandler["common"]["logLevel"],
    True
    if confHandler is None or confHandler["common"]["enableTerminalLog"] is None
    else confHandler["common"]["enableTerminalLog"] == "true",
    False
    if confHandler is None or confHandler["common"]["enableLogFile"] is None
    else confHandler["common"]["enableLogFile"] == "true",
    "exec.log"
    if confHandler is None or confHandler["common"]["logFileName"] is None
    else confHandler["common"]["logFileName"],
)
if confHandler is None:
    exit(2)


celeryHandler: celery.Celery = celery.Celery(
    "mainTask",
    broker="amqp://"
    + confHandler["rabbitmq"]["user"]
    + ":"
    + confHandler["rabbitmq"]["pass"]
    + "@"
    + confHandler["rabbitmq"]["addr"]
    + ":"
    + confHandler["rabbitmq"]["port"]
    + "//"
    + confHandler["rabbitmq"]["vhost"],
    backend="redis://"
    + confHandler["redis"]["addr"]
    + ":"
    + confHandler["redis"]["port"],
    include=["main"],
)


@celeryHandler.task
def mainWorker(dev: InputStruct, scriptAndFormater: dict[str, str]):
    scriptList = list(scriptAndFormater.keys())
    triggers = {}
    if confHandler is not None and confHandler["common"]["enableLog"] == "true":
        triggers["afterExecuteOneCmd"] = afterExecuteOneCmdLog
        triggers["beforeReturn"] = beforeReturnLog
        triggers["beforeConnect"] = beforeConnectLog
        triggers["onAuthFaild"] = connectFaild
        triggers["onNetTimeOut"] = connectFaild
        triggers["onTypeForkExec"] = typeForkExec
        triggers["onSSHException"] = connectFaild
        triggers["onUnknowException"] = connectFaild
    result = DevExec(dev, scripts=scriptList, triggers=triggers).run()
    if result.get("status") != 5:
        return result
    result = result.get("result")
    results = {}
    results["status"] = 1
    if isinstance(result, dict):
        cmds = result.keys()
        for i in cmds:
            results[i] = formaterProc(result[i], scriptAndFormater[i])
    return results


def formaterProc(result: str, formaterName: str):
    if not formaterName:
        return result
    templaRoot = os.path.join(os.path.dirname(__file__), "textfsmLib")
    if isinstance(result, str):
        return Formater(templateFileName=formaterName, templateRoot=templaRoot).run(
            result
        )


def afterExecuteOneCmdLog(ctx: DevExec, cmd: str):
    logger.debug("afterExecuteOneCmd: " + cmd)


def beforeReturnLog(ctx: DevExec):
    logger.debug(
        "ready to return result:" + "(not valid log data type: %s)" % type(ctx.result)
        if type(ctx.result) is not str
        else ctx.result
    )


def beforeConnectLog(ctx: DevExec):
    logger.debug("ready to connect target: " + ctx.devInfo.get("ip"))
    TFECmd = list(TFEDevFuncMap.keys())
    if ctx.devInfo.get("device_type") in TFECmd:
        raise TypeForkExec


def connectFaild(ctx: DevExec, err: Exception):
    logger.warn("%s during connect with %s", err, ctx.devInfo.get("ip"))


def typeForkExec(ctx: DevExec):
    cmds = ctx.scripts
    if cmds is None or len(cmds) == 0:
        ctx.result = {"msg": "cmds required"}
        return
    TFECmd = ctx.devInfo.get("device_type")
    cmdFuncMap = TFEDevFuncMap[TFECmd]
    for cmd in cmds:
        if cmd not in cmdFuncMap:
            continue
        result = cmdFuncMap[cmd](
            ctx.devInfo.get("ip"),
            ctx.devInfo.get("username"),
            ctx.devInfo.get("password"),
        )
        if result.get("status") == 1000:
            ctx.result[cmd] = result.get("result")
        else:
            ctx.result[cmd] = {"msg": result.get("msg")}

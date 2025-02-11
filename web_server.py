from fastapi import FastAPI
from enum import Enum
from pydantic import BaseModel
from typing import Dict
import task

appMain = FastAPI()


class statusCode(Enum):
    Ok = 0


@appMain.get("/ping")
def ping():
    return {"status": statusCode.Ok, "data": "Pong!"}


class CmdReq(BaseModel):
    target: str
    username: str
    password: str
    devtype: str
    encoding: str
    cmds: Dict[str, str]


@appMain.post("/cmd")
def normalCommand(cmd: CmdReq):
    resultText = task.mainWorker.delay(
        {
            "ip": cmd.target,
            "username": cmd.username,
            "password": cmd.password,
            "device_type": cmd.devtype,
            "encoding": cmd.encoding,
            "session_log": "session.log",
        },
        cmd.cmds,
    )
    while not resultText.ready():
        pass
    return {"status": statusCode.Ok, "data": resultText.get()}

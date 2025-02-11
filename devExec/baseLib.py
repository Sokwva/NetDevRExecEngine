from typing import Callable
import netmiko
import netmiko.exceptions
from devExec.common import send_command_for_no_disable_paging, InputStruct, OutputStruct


def passby():
    pass


specialProcMethod: dict[str, Callable] = {
    "no_disable_paging": send_command_for_no_disable_paging,
}


class TypeForkExec(Exception):
    pass


class DevExec:
    def __init__(
        self,
        devInfo: InputStruct,
        scripts: list[str],
        triggers: dict[str, Callable] = {},
    ) -> None:
        self.devInfo = devInfo
        self.scripts = scripts

        self.triggers: dict[str, Callable] = {} if len(triggers) == 0 else triggers
        if "specialCmd" not in devInfo:
            self.specialCmd: str = ""
        else:
            self.specialCmd: str = devInfo["specialCmd"]
            del devInfo["specialCmd"]

        self.result = {}

    def run(self) -> OutputStruct:
        try:
            self.triggers["beforeConnect"](
                self
            ) if "beforeConnect" in self.triggers else passby()
            conn: netmiko.BaseConnection = netmiko.ConnectHandler(**self.devInfo)

            self.triggers["beforeExecute"](
                self
            ) if "beforeExecute" in self.triggers else passby()

            for cmd in self.scripts:
                if len(self.specialCmd) == 0:
                    self.result[cmd] = conn.send_command(cmd, cmd_verify=False)
                else:
                    self.triggers["beforeSpecialMethod"](
                        self
                    ) if "beforeSpecialMethod" in self.triggers else passby()
                    self.result[cmd] = specialProcMethod[self.specialCmd](
                        self.devInfo, self.scripts
                    )

                    self.triggers["afterSpecialMethod"](
                        self
                    ) if "afterSpecialMethod" in self.triggers else passby()

                self.triggers["afterExecuteOneCmd"](
                    self, cmd
                ) if "afterExecuteOneCmd" in self.triggers else passby()

            self.triggers["afterExecute"](
                self
            ) if "afterExecute" in self.triggers else passby()
            conn.cleanup()

            self.triggers["afterDisconnect"](
                self
            ) if "afterExecute" in self.triggers else passby()
        except netmiko.exceptions.AuthenticationException as e:
            self.triggers["onAuthFaild"](
                self, e
            ) if "onAuthFaild" in self.triggers else passby()
            return {"status": 2, "result": None}
        except netmiko.exceptions.NetmikoTimeoutException as e:
            self.triggers["onNetTimeOut"](
                self, e
            ) if "onNetTimeOut" in self.triggers else passby()
            return {"status": 3, "result": None}
        except netmiko.exceptions.SSHException as e:
            self.triggers["onSSHException"](
                self, e
            ) if "onSSHException" in self.triggers else passby()
            return {"status": 4, "result": None}
        except TypeForkExec:
            self.triggers["onTypeForkExec"](
                self
            ) if "onTypeForkExec" in self.triggers else passby()
            return {"status": 1000, "result": self.result}
        except Exception as e:
            self.triggers["onUnknowException"](
                self, e
            ) if "onUnknowException" in self.triggers else passby()
            return {"status": 100, "result": None}
        else:
            self.triggers["beforeReturn"](
                self
            ) if "beforeReturn" in self.triggers else passby()
            return {"status": 5, "result": self.result}

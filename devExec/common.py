from typing import TypedDict, NotRequired, Any, Optional
import netmiko
import re
import time


class InputStruct(TypedDict):
    ip: str
    username: str
    password: str
    device_type: str
    session_log: str
    encoding: str
    specialCmd: NotRequired[str]


class OutputStruct(TypedDict):
    status: int
    result: Optional[dict[Any, Any]]

# src:https://blog.csdn.net/xdy762024688/article/details/131779480
def send_command_for_no_disable_paging(dev, cmd):
    with netmiko.ConnectHandler(**dev) as conn:
        # 存放回显的变量
        output = ""
        # 判断回显结束的正则
        output_end_pattern = r"<\S+>"
        # 判断分页交互的正则
        more_pattern = "----More----"

        # 超时时间，隧道中读取内容的间隔时间，根据二者计算的循环次数
        timeout = conn.timeout
        loop_delay = 0.2
        loops = timeout / loop_delay
        i = 0
        # 通过write_channel发送命令，命令后追加一个回车换行符
        conn.write_channel("{}{}".format(cmd, conn.RETURN))
        # 进入循环，读取隧道中信息
        while i <= loops:
            # 读取隧道中的信息，放入chunk_output
            chunk_output = conn.read_channel()
            # 判断是否有分页交互提示
            if more_pattern in chunk_output:
                # 回显中的分页提示去除,去除一些影响回显展示的空格
                chunk_output = chunk_output.replace(more_pattern, "").replace(
                    "               ", ""
                )
                # 拼接回显
                output += chunk_output
                # 发送回车换行符
                conn.write_channel(conn.RETURN)
            # 根据提示符判断是否回显结束
            elif re.search(output_end_pattern, chunk_output):
                # 拼接回显 并跳出循环
                output += chunk_output
                break
            # 停顿loop_delay秒
            time.sleep(loop_delay)
            # 计数器i加一 类似其他语言中的i++
            i += 1
        # 如果超过了，则证明超时，我们可以自己抛出异常
        if i > loops:
            raise Exception('执行命令"{}"超时'.format(cmd))
        return output

import pynetbox
import requests
import urllib3

urllib3.disable_warnings()

handler:pynetbox.api
handlerOk = False

def init(target:str,token:str)->bool:
    global handler,handlerOk
    session = requests.Session()
    session.verify = False
    handler = pynetbox.api(target,token)
    handler.http_session = session
    try:
        handler.status()
    except Exception:
        return False
    else:
        handlerOk = True
        return True

def queryIPaddrExist(ip:str,maskLen="24"):
    resp = handler.ipam.ip_addresses.filter(ip+"/"+maskLen)
    return len(resp)

def addIPaddr(ip:str,status:str="active"):
    handler.ipam.ip_addresses.create(address=ip,status=status)

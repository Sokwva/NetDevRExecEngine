import os,textfsm

class Formater:
    def __init__(self, templateFileName: str, templateRoot: str = "") -> None:
        self.textfsmLibRoot: str = templateRoot if templateRoot != "" else os.path.join(os.path.dirname(__file__), "textfsmLib")
        self.templateFileName: str = templateFileName
        
        self.result = {}

    def run(self, rawText: str):
        with open(os.path.join(self.textfsmLibRoot, self.templateFileName)) as f:
            template = textfsm.TextFSM(f)
            return template.ParseTextToDicts(rawText)

import os
import lib

ENABLE_LOG = True

if __name__ == '__main__':
    basePath = os.path.abspath(os.path.dirname(__file__))
    workFilePath = os.path.join(basePath, "test.xlsx")
    x = lib.DeviceExcel(workFilePath)
    fail_list = x.run()
    if fail_list.__len__() > 0:
        print(fail_list)

import re
from log import *

def checkIsDigit(input_str):
    authLog.info(f"String successfully validated {input_str}, checkIsDigit function.")
    return input_str.strip().isdigit()
    #if input_str.strip().isdigit():
    #    return True
    #else:
    #    return False

def validateIP(deviceIP):
    validIP_Pattern = r'^(\d{1,3})\.(\d{1,3})\.(\d{1,3})\.(\d{1,3})$'
    if re.match(validIP_Pattern, deviceIP):
        authLog.info(f"IP successfully validated {deviceIP}")
        return all(0 <= int(num) <= 255 for num in deviceIP.split('.'))
    return False
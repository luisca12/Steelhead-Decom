import re
from log import *

def checkIsDigit(input_str):
    try:
        authLog.info(f"String successfully validated selection number {input_str}, from checkIsDigit function.")
        return input_str.strip().isdigit()
    
    except Exception as error:
        authLog.error(f"Invalid option chosen: {input_str}, error: {error}\n")

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
                
def delStringFromFile(filePath, stringToDel):
    with open(filePath, "r") as file:
        file_content = file.read()

    updated_content = file_content.replace(stringToDel, "")

    with open(filePath, "w") as file:
        file.write(updated_content)
from netmiko import ConnectHandler
from log import *
from strings import *
from auth import *
import logging
import os

shRun = "show run"
shWCCP = "show run | i wccp" 
shWCCP1 = "show run | i wccp|interface"      
shWCCP2 = "show run interface vlan1700"

def shCommands(validIPs, username, netDevice, printNotConnect=True):
    # This function is to show the interfaces not connected.
    # show interface status | include Port | notconnect
    try:
        for validDeviceIP in validIPs:
            validDeviceIP = validDeviceIP.strip()
            currentNetDevice = {
                'device_type': 'cisco_ios',
                'ip': validDeviceIP,
                'username': username,
                'password': netDevice['password'],
                'secret': netDevice['secret']
            }

            print(f"Connecting to device {validDeviceIP}...")
            with ConnectHandler(**currentNetDevice) as sshAccess:
                sshAccess.enable()

                # Will first take a show run
                shRunString(validDeviceIP)
                shRunOut = sshAccess.send_command(shRun)
                configChangeLog.info(f"User {username} connected to device {validDeviceIP}")
                configChangeLog.info(f"Automation ran the command \"{shRun}\" into the device {validDeviceIP} "\
                    f"successfully:\n{shRunOut}")
                print("Show run successfully taken and saved into configChangesLog.txt\n")

                shWCCPout = sshAccess.send_command(shWCCP)
                authLog.info(f"Automation ran the command \"{shWCCP}\" into the device {validDeviceIP} successfully")                
                shWCCP1out = sshAccess.send_command(shWCCP1)
                authLog.info(f"Automation ran the command \"{shWCCP1}\" into the device {validDeviceIP} successfully")                
                shWCCP2out = sshAccess.send_command(shWCCP2)
                authLog.info(f"Automation ran the command \"{shWCCP2}\" into the device {validDeviceIP} successfully")
                with open(f"{validDeviceIP}_Outputs.txt", "a") as file:
                    file.write(f"User {username} connected to device IP {validDeviceIP}, ")
                    file.write(f"{shWCCP}:\n{shWCCPout}\n")
                    file.write(f"{shWCCP1}:\n{shWCCP1out}\n")
                    file.write(f"{shWCCP2}:\n{shWCCP2out}\n")            

    except Exception as error:
        print(f"An error occurred: {error}")
        authLog.error(f"User {username} connected to {validDeviceIP} got an error: {error}\n")
        return []
    
    finally:
        print("Outputs and files successfully created.")
        print("For any erros or logs please check authLog.txt\n")
        os.system("PAUSE")
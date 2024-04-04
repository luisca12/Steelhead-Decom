from netmiko import ConnectHandler
from log import *
from strings import *
from auth import *
import logging
import os

shRun = "show run"
shInt = "show run interface "
shHostname = "show run | i hostname"

shWCCP = "show run | i ip wccp" 
shWCCP1 = "show run | i wccp|interface"      
shWCCP2 = "show run interface vlan1700"
shWCCP3 = "show run interface vlan1700 | inc ip add"
shWCCP4 = "show mac add | inc Mac Address T|Vlan|---|1700|000e.b6"

intPatt = r'\b(?:Et|Gi|Te)\d+\/\d+(?:\/\d+)?(?:-\d+)?(?:, (?:Et|Gi|Te)\d\/\d+(?:\/\d+)?(?:-\d+)?)*\b'

defaultInt = "default interface "

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
                configChangeLog.info(f"Automation ran the command \"{shRun}\" into the device {validDeviceIP} successfully")
                with open(f"{validDeviceIP}_showRun.txt", "a") as file:
                    file.write(f"User {username} connected to device IP {validDeviceIP}\n")
                    file.write(f"{shRunOut}\n")
                print(f"Show run successfully taken and saved into {validDeviceIP}_showRun.txt\n")


                print(f"Starting to take other outputs, saved into {validDeviceIP}_ImplementationPlan.txt")
                shHostnameOut = sshAccess.send_command(shHostname)
                shHostnameOut = shHostnameOut.replace('hostname', '')
                shHostnameOut = shHostnameOut.strip()

                shWCCPout = sshAccess.send_command(shWCCP)
                authLog.info(f"Automation ran the command \"{shWCCP}\" into the device {validDeviceIP} successfully")                
                shWCCP1out = sshAccess.send_command(shWCCP1)
                authLog.info(f"Automation ran the command \"{shWCCP1}\" into the device {validDeviceIP} successfully")                
                shWCCP2out = sshAccess.send_command(shWCCP2)
                authLog.info(f"Automation ran the command \"{shWCCP2}\" into the device {validDeviceIP} successfully")
                shWCCP3out = sshAccess.send_command(shWCCP3)
                authLog.info(f"Automation ran the command \"{shWCCP3}\" into the device {validDeviceIP} successfully")
                shWCCP4out = sshAccess.send_command(shWCCP4)
                authLog.info(f"Automation ran the command \"{shWCCP4}\" into the device {validDeviceIP} successfully")

                print(shWCCP3out, "\n\n")
                matchIPv4 = re.search(r'(\b(?!255\.)\d{1,3}\.\d{1,3}\.\d{1,3}\.)\d{1,3}\b', shWCCP3out)
                print(matchIPv4,"\n\n")
                if matchIPv4:
                    extractedIP = matchIPv4.group(1) + "*"
                    authLog.info(f"Succesfully found IP address: {extractedIP}")
                else:
                    extractedIP = "No IP address found"
                    authLog.error(f"No IP address found by variable \"matchIPv4\" from the command {shWCCP3}, string found: {matchIPv4}")

                shBGP = f"show run | inc router bgp | {extractedIP}"
                print(shBGP,"\n\n")
                shBGPOut = sshAccess.send_command(shBGP)
                print(shBGPOut,"\n\n")
                authLog.info(f"Automation ran the command \"{shBGP}\" into the device {validDeviceIP} successfully, " \
                             f"output of the command:\n{shBGPOut}") 
                shBGPOut = "\n".join([line for line in shBGPOut.split("\n") if not line.strip().startswith("ip address")])
                authLog.info(f"Successfully removed \"ip address\" from the previous output, new output:\n{shBGPOut}")
                
                matchMAC = re.findall(intPatt, shWCCP4out) 

                with open(f"{validDeviceIP}_Outputs.txt", "a") as file:
                    file.write(f"\nUser {username} connected to device IP {validDeviceIP}\n")
                    file.write(f"\n{shHostnameOut}#{shWCCP}\n{shWCCPout}\n")
                    file.write(f"\n{shHostnameOut}#{shWCCP1}\n{shWCCP1out}\n")
                    file.write(f"\n{shHostnameOut}#{shWCCP2}\n{shWCCP2out}\n")   
                    file.write('\t########################## Implementation Plan #########################')
                    file.write('\nTry to SSH to the steelhead and if it fails try to connect through the open gear {open gear IP}:\n') 
                    file.write('\t{steelhead-Hostname}    {steelhead-IP}\n')     
                    file.write('\t{steelhead-Hostname}    {steelhead-IP}\n')
                    file.write('\nOnce in the CLI go to enable and run this command:\n')
                    file.write('\treset factory reload\n\n')
                    file.write('******************************** make sure the ACCL are factory default before starting this part ******************************\n') 
                    file.write("SSH to the Core SW: \n\n")
                    shWCCPout1 = shWCCPout.replace('ip', 'no ip')
                    shWCCP2out1 = shWCCP2out.replace('ip', 'no ip')
                    file.write(f"{shWCCPout1}\n\n")
                    file.write(f"{shWCCP2out1}\n\n")     
                    file.write("Upon removing WCCP from the SVIs remove the VLAN, SVI and network on BGP for VLAN1700\n\n")
                    shBGPOut1 = shBGPOut.replace('network', 'no network')
                    file.write(f"{shBGPOut1}\n\n")
                    file.write("no vlan 1700\n\n")
                    file.write("no interface 1700\n\n")
                    file.write(f"{shWCCP4out}\n\n")

                    for interface in matchMAC:
                        shIntCmd = f"{shInt}{interface}"
                        matchMACout = sshAccess.send_command(shIntCmd)   
                        file.write(f"{matchMACout}\n\n")
                    
                    for interface in matchMAC:
                        defaultIntCmd = f"{defaultInt}{interface}\n"  
                        file.write(f"\n{defaultIntCmd}\n")
                        file.write(f"interface {interface}\n")
                        file.write("description unusedPort\n")
                        file.write("switchport mode access\n")
                        file.write("switchport access vlan 1001\n")
                        file.write("shutdown\n\n")

    except Exception as error:
        print(f"An error occurred: {error}")
        authLog.error(f"User {username} connected to {validDeviceIP} got an error: {error}\n")
        return []
    
    finally:
        print("Outputs and files successfully created.")
        print("For any erros or logs please check authLog.txt\n")
        os.system("PAUSE")
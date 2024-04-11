from netmiko import ConnectHandler
from functions import *
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
buildConfigPatt = r"Building configuration\.\.\.\n\nCurrent configuration : \d+ bytes\n!"
shWCCP1Patt = r"interface [a-zA-Z0-9\/]+[\r\n\s]+ip wccp \d+ redirect in"

defaultInt = "default interface "

def shRunIntCmd(CLIcmd):
    CLIcmdOut = CLIcmd   
    CLIcmdOutLines = CLIcmdOut.split("\n")
    CLIcmdOutIndex = next((i for i, line in enumerate(CLIcmdOutLines) if "interface" in line), None)
    CLIcmdOut = "\n".join(CLIcmdOutLines[CLIcmdOutIndex:])
    return CLIcmdOut

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
                shWCCP2out = shRunIntCmd(shWCCP2out)
                authLog.info(f"Automation ran the command \"{shWCCP2}\" into the device {validDeviceIP} successfully")
                shWCCP3out = sshAccess.send_command(shWCCP3)
                shWCCP3out = shRunIntCmd(shWCCP3out)
                authLog.info(f"Automation ran the command \"{shWCCP3}\" into the device {validDeviceIP} successfully")
                shWCCP4out = sshAccess.send_command(shWCCP4)
                shWCCP4out = shRunIntCmd(shWCCP4out)
                authLog.info(f"Automation ran the command \"{shWCCP4}\" into the device {validDeviceIP} successfully")

                shWCCP1outPatt = re.finditer(shWCCP1Patt, shWCCP1out)
                shWCCP1out = '\n'.join(match.group(0) for match in shWCCP1outPatt)

                matchIPv4 = re.search(r'(\b(?!255\.)\d{1,3}\.\d{1,3}\.\d{1,3}\.)\d{1,3}\b', shWCCP3out)

                if matchIPv4:
                    extractedIP = matchIPv4.group(1) + "*"
                    authLog.info(f"Succesfully found IP address: {extractedIP}")
                else:
                    extractedIP = "No IP address found"
                    authLog.error(f"No IP address found by variable \"matchIPv4\" from the command {shWCCP3}, string found: {matchIPv4}")

                shBGP = f"show run | inc router bgp | {extractedIP}"
                shBGPOut = sshAccess.send_command(shBGP)
                shBGPOutLines = shBGPOut.split("\n")
                bgpIndex = next((i for i, line in enumerate(shBGPOutLines) if "router bgp" in line), None)
                if bgpIndex is not None:
                    shBGPOut = "\n".join(shBGPOutLines[bgpIndex:])
                authLog.info(f"Automation ran the command \"{shBGP}\" into the device {validDeviceIP} successfully, " \
                             f"output of the command:\n{shBGPOut}") 
                shBGPOut = "\n".join([line for line in shBGPOut.split("\n") if not line.strip().startswith("ip address")])
                authLog.info(f"Successfully removed \"ip address\" from the previous output, new output:\n{shBGPOut}")
                
                matchMAC = re.findall(intPatt, shWCCP4out) 

                with open(f"{validDeviceIP}_Outputs.txt", "a") as file:
                    file.write(f"User {username} connected to device IP {validDeviceIP}\n\n")
                    file.write('  =======================================\n')
                    file.write('   Below we check for WCCP configuration\n')
                    file.write('  =======================================')
                    file.write(f"\n{shHostnameOut}#{shWCCP}\n{shWCCPout}\n")
                    file.write(f"\n{shHostnameOut}#{shWCCP1}\n{shWCCP1out}\n")
                    file.write(f"\n{shHostnameOut}#{shWCCP2}\n{shWCCP2out}\n")   
                    file.write('\t########################## Implementation Plan #########################')
                    file.write('\nTry to SSH to the steelhead and if it fails try to connect through the open gear {open gear IP}:\n') 
                    file.write('\t{steelhead-Hostname}    {steelhead-IP}\n')     
                    file.write('\t{steelhead-Hostname}    {steelhead-IP}\n')
                    file.write('\nOnce in the CLI go to enable and run this command:\n')
                    file.write('\treset factory reload\n\n')
                    file.write('  ==================================================================\n')
                    file.write('   Make sure the ACCL are factory default before starting this part\n')
                    file.write('  ==================================================================\n')
                    file.write("SSH to the Core SW: \n\n")
                    shWCCPout1 = shWCCPout.replace('ip wccp 51 redirect in', '')
                    shWCCPout1 = shWCCPout1.replace('ip wccp 52 redirect in', '')
                    shWCCPout1 = shWCCPout1.replace('ip', 'no ip')
                    shWCCP1out1 = shWCCP1out.replace('ip', 'no ip')
                    shWCCP2out1 = shWCCP2out.replace('ip address', 'no ip address')
                    file.write(f"{shWCCPout1}\n\n")
                    file.write(f"{shWCCP1out1}\n\n")
                    file.write(f"{shWCCP2out1}\n")
                    file.write('  =======================================================================================\n')     
                    file.write("   Upon removing WCCP from the SVIs remove the VLAN, SVI and network on BGP for VLAN1700\n")
                    file.write('  =======================================================================================\n')
                    shBGPOut1 = shBGPOut.replace('network', 'no network')
                    file.write(f"{shBGPOut1}\n\n")
                    file.write("no vlan 1700\n\n")
                    file.write("no interface 1700\n\n")
                    file.write('  ========================================================================================\n')
                    file.write("   Below are the Interfaces where the steelheads are connected and interfaces in VLAN1700\n")
                    file.write('\t\t\t\t\t\t\tSteelhead MAC Address: 000e.b6\n')
                    file.write('  ========================================================================================\n')
                    if "1700" not in shWCCP4out and "000e.b6" not in shWCCP4out:
                        file.write("\nThere are no physical interfaces in VLAN 1700 nor any steelhead device connected")
                    else:
                        file.write(f"{shWCCP4out}\n\n")

                        for interface in matchMAC:
                            shIntCmd = f"{shInt}{interface}"
                            matchMACout = sshAccess.send_command(shIntCmd) 
                            matchMACout = shRunIntCmd(matchMACout)  
                            file.write(f"{matchMACout}\n")
                        file.write('  ====================================================\n')
                        file.write('   Below is the final configuration of the interfaces\n')
                        file.write('  ====================================================\n')
                        file.write("NOTE: If this is empty, no physical interfaces will be modified.\n\n")
                        for interface in matchMAC:
                            defaultIntCmd = f"{defaultInt}{interface}"
                            file.write(f"{defaultIntCmd}\n")
                            file.write(f"interface {interface}\n")
                            file.write("description unusedPort\n")
                            file.write("switchport mode access\n")
                            file.write("switchport access vlan 1001\n")
                            file.write("shutdown\n")

    except Exception as error:
        print(f"An error occurred: {error}")
        authLog.error(f"User {username} connected to {validDeviceIP} got an error: {error}\n")
        return []
    
    finally:
        print("Outputs and files successfully created.")
        print("For any erros or logs please check authLog.txt\n")
        os.system("PAUSE")
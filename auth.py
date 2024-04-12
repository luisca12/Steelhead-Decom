from netmiko import ConnectHandler
from netmiko.exceptions import NetMikoAuthenticationException, NetMikoTimeoutException
from functions import *
from log import *
import socket

username = ""
execPrivPassword = ""
netDevice = {}
validIPs = []

def Auth():
    global username, execPrivPassword, netDevice, validIPs

    while True:
        deviceIPs = input("Please enter the devices IPs separated by commas: ")
        deviceIPsList = deviceIPs.split(',')

        for ip in deviceIPsList:
            ip = ip.strip()
            if validateIP(ip):
                try:
                    connTest = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    connTest.settimeout(3)
                    connResult = connTest.connect_ex((ip, 22))
                    if connResult == 0:
                        validIPs.append(ip)
                        print(f"Device {ip} is reachable on port TCP 22.")
                        authLog.info(f"Device {ip} is reachable on port TCP 22.")
                    else:
                        print(f"Device {ip} is not reachable on port TCP 22, will be skipped.\n")
                        authLog.error(f"Device IP: {ip}, is not reachable on port TCP 22.")
                except Exception as error:
                    print("Error occurred while checking device reachability:", error,"\n")
                    authLog.error(f"Error occurred while checking device reachability for IP {ip}: {error}")
            else:
                print(f"Invalid IP address format: {ip}, will be skipped.")
                authLog.error(f"User {username} input the following invalid IP: {ip}")
        if validIPs:
            break

    while True:
        try:
            username = input("Please enter your unsername: ")
            password = input("Please enter your password: ")
            execPrivPassword = input("Pleae input your enable password: ")

            for deviceIP in validIPs:
                netDevice = {
                    'device_type' : 'cisco_xe',
                    'ip' : deviceIP,
                    'username' : username,
                    'password' : password,
                    'secret' : execPrivPassword
                }

                sshAccess = ConnectHandler(**netDevice)
                sshAccess.enable()
                print(f"Login successful! Logged to device {deviceIP} \n")

                authLog.info(f"Successful login - remote device IP: {deviceIP}, Username: {username}")

            return validIPs, username, netDevice

        except NetMikoAuthenticationException:
            print("\n Login incorrect. Please check your username and password")
            print(" Retrying operation... \n")
            authLog.error(f"Failed to authenticate - remote device IP: {deviceIP}, Username: {username}")

        except NetMikoTimeoutException:
            print("\n Connection to the device timed out. Please check your network connectivity and try again.")
            print(" Retrying operation... \n")
            authLog.error(f"Connection timed out, device not reachable - remote device IP: {deviceIP}, Username: {username}\n")
                       
        except socket.error:
            print("\n IP address is not reachable. Please check the IP address and try again.")
            print(" Retrying operation... \n")
            authLog.error(f"Remote device unreachable - remote device IP: {deviceIP}, Username: {username}\n")
import os
from auth import *

def greetingString():
        os.system("CLS")
        print('  ------------------------------------------------- ')
        print("   Welcome to the automated show commands program ")
        print('  ------------------------------------------------- ')

def menuString(deviceIP, username):
        os.system("CLS")
        print("Connected to:", deviceIP, "as", username)
        print('\n  -------------------------------------------------------------- ')
        print('\t\tMenu - Please choose an option ')
        print('  -------------------------------------------------------------- ')
        print('>\t     1. To take the following show commands:           <')
        print('\t  show run | i wccp, show run | i wccp|interface\t')
        print('\t\t   show run interface vlan1700\n')          
        print('>\t\t\t2. Exit the program\t\t     <')
        print('\n  -------------------------------------------------------------- ')

def inputErrorString():
        os.system("CLS")
        print('  ------------------------------------------------- ')  
        print('>      INPUT ERROR: Only numbers are allowed       <')
        print('  ------------------------------------------------- ')

def shRunString(validIPs):
        print('  ------------------------------------------------- ')  
        print(f'> Taking a show run of the device {validIPs} <')
        print('>\t   Please wait until it finishes\t  <')
        print('  ------------------------------------------------- ')

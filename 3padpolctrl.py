# -*- coding: utf-8 -*-
"""
Created on Wed Oct  4 20:16:26 2023

@author: ektop
"""

import clr
import time

clr.AddReference("C:\\Program Files\\Thorlabs\\Kinesis\\Thorlabs.MotionControl.DeviceManagerCLI.dll")
clr.AddReference("C:\\Program Files\\Thorlabs\\Kinesis\\Thorlabs.MotionControl.GenericMotorCLI.dll")
clr.AddReference("C:\\Program Files\\Thorlabs\\Kinesis\\ThorLabs.MotionControl.PolarizerCLI.dll")

from Thorlabs.MotionControl.DeviceManagerCLI import *
from Thorlabs.MotionControl.GenericMotorCLI import *
from Thorlabs.MotionControl.PolarizerCLI import *
from System import Decimal

    # Uncomment this line if you are using a simulation
    #SimulationManager.Instance.InitializeSimulations()



# Build device list. 
DeviceManagerCLI.BuildDeviceList()
# create new device.
serial_no = "38392094"
device = Polarizer.CreatePolarizer(serial_no)
# Connect to device.
device.Connect(serial_no)
# Ensure that the device settings have been initialized.
device.WaitForSettingsInitialized(10000)  # 10 second timeout.
assert device.IsSettingsInitialized() is True
# Start polling loop and enable device.
device.StartPolling(250)  #250ms polling rate.
time.sleep(5)
device.EnableDevice()
time.sleep(0.25)  # Wait for device to enable.
# Get Device Information and display description.
device_info = device.GetDeviceInfo()
print(device_info.Description)
# Call device methods.
print("Homing Device")
paddle1 = PolarizerPaddles.Paddle1#choose 1st paddle
device.Home(paddle1,60000)  # 60 second timeout.
        
paddle2 = PolarizerPaddles.Paddle2#choose 2nd paddle
device.Home(paddle2,60000)  # 60 second timeout.
print("Done")
time.sleep(2)

paddle3 = PolarizerPaddles.Paddle3#choose 3rd paddle
device.Home(paddle3,60000)  # 60 second timeout.
print("Done")
time.sleep(2)

new_pos1 = Decimal(20.0)  # Must be a .NET decimal.
new_pos2 = Decimal(50.0)  # Must be a .NET decimal.
new_pos3 = Decimal(100.0)  # Must be a .NET decimal.

print(f'Moving to {new_pos1}')
device.MoveTo(new_pos1,paddle1, 60000)  # 60 second timeout.
print("Done")

print(f'Moving to {new_pos2}')
device.MoveTo(new_pos2,paddle2, 60000)  # 60 second timeout.
print("Done")

print(f'Moving to {new_pos3}')
device.MoveTo(new_pos3,paddle3, 60000)  # 60 second timeout.
print("Done")
        # Stop polling loop and disconnect device before program finishes. 
        #device.StopPolling()
        #device.Disconnect()
        
        

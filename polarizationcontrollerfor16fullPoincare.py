# -*- coding: utf-8 -*-
"""
Created on Wed Jan 24 13:46:19 2024

@author: ektop
"""

"""
Created on Thu Oct  5 18:02:02 2023
Modified on [Januray 2024]
@author: ektop
"""
import os
import sys
import clr
import time

clr.AddReference("C:\\Program Files\\Thorlabs\\Kinesis\\Thorlabs.MotionControl.DeviceManagerCLI.dll")
clr.AddReference("C:\\Program Files\\Thorlabs\\Kinesis\\Thorlabs.MotionControl.GenericMotorCLI.dll")
clr.AddReference("C:\\Program Files\\Thorlabs\\Kinesis\\ThorLabs.MotionControl.PolarizerCLI.dll")

from Thorlabs.MotionControl.DeviceManagerCLI import *
from Thorlabs.MotionControl.GenericMotorCLI import *
from Thorlabs.MotionControl.PolarizerCLI import *
from System import Decimal

# Define the measurement angles for the Full Poincare sphere basis
measurement_angles = [
    Decimal(0.0),  # Horizontal
    Decimal(45.0),  # +45 degrees
    Decimal(90.0),  # Vertical
    Decimal(135.0),  # -45 degrees
    Decimal(180.0),  # Horizontal
    Decimal(225.0),  # +45 degrees
    Decimal(270.0),  # Vertical
    Decimal(315.0),  # -45 degrees
    Decimal(0.0),  # Horizontal
    Decimal(45.0),  # +45 degrees
    Decimal(90.0),  # Vertical
    Decimal(135.0),  # -45 degrees
    Decimal(180.0),  # Horizontal
    Decimal(225.0),  # +45 degrees
    Decimal(270.0),  # Vertical
    Decimal(315.0),  # -45 degrees
]

RUN = True

while RUN:
    try:
        # Build device list.
        DeviceManagerCLI.BuildDeviceList()

        # Create new device.
        serial_no = "38390544"
        device = Polarizer.CreatePolarizer(serial_no)

        # Connect to device.
        device.Connect(serial_no)

        # Ensure that the device settings have been initialized.
        if not device.IsSettingsInitialized():
            device.WaitForSettingsInitialized(10000)  # 10 second timeout.
            assert device.IsSettingsInitialized() is True

        # Start polling loop and enable device.
        device.StartPolling(250)  # 250ms polling rate.
        time.sleep(5)
        device.EnableDevice()
        time.sleep(0.25)  # Wait for device to enable.

        # Get Device Information and display description.
        device_info = device.GetDeviceInfo()
        print(device_info.Description)

        for angle in measurement_angles:
            print(f"Moving to {angle} degrees")
            device.MoveTo(angle, PolarizerPaddles.Paddle1, 60000)  # 60 second timeout.
            print("Done")
            time.sleep(2)  # Wait for stabilization

            # Perform measurement here
            # [INSERT CODE FOR MEASUREMENT]

        # Stop polling loop and disconnect device before program finishes.
        device.StopPolling()
        device.Disconnect()

        # Connect to device.
        device.Connect(serial_no)

        restart = input("\nDo you want to restart the program? [y/n] > ")
        if restart == "y":
            os.execl(sys.executable, os.path.abspath(__file__), *sys.argv)
        else:
            print("\nThe program will be closed...")
            sys.exit(0)

    except Exception as e:
        print(e)
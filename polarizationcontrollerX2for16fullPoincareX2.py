# -*- coding: utf-8 -*-
"""
Created on Tue Jan 30 11:48:39 2024

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

        # Create new devices.
        serial_no1 = "38390544"  # Serial number of the first polarization controller
        serial_no2 = "38392094"  # Serial number of the second polarization controller
        device1 = Polarizer.CreatePolarizer(serial_no1)
        device2 = Polarizer.CreatePolarizer(serial_no2)

        # Connect to devices.
        device1.Connect(serial_no1)
        device2.Connect(serial_no2)

        # Ensure that the device settings have been initialized.
        if not device1.IsSettingsInitialized():
            device1.WaitForSettingsInitialized(10000)  # 10 second timeout.
            assert device1.IsSettingsInitialized() is True

        if not device2.IsSettingsInitialized():
            device2.WaitForSettingsInitialized(10000)  # 10 second timeout.
            assert device2.IsSettingsInitialized() is True

        # Start polling loop and enable devices.
        device1.StartPolling(250)  # 250ms polling rate.
        device2.StartPolling(250)  # 250ms polling rate.
        time.sleep(5)
        device1.EnableDevice()
        device2.EnableDevice()
        time.sleep(0.25)  # Wait for devices to enable.

        # Get Device Information and display description.
        device_info1 = device1.GetDeviceInfo()
        device_info2 = device2.GetDeviceInfo()
        print(device_info1.Description)
        print(device_info2.Description)

        for angle in measurement_angles:
            print(f"Moving to {angle} degrees")
            device1.MoveTo(angle, PolarizerPaddles.Paddle1, 60000)  # 60 second timeout.
            device2.MoveTo(angle, PolarizerPaddles.Paddle1, 60000)  # 60 second timeout.
            print("Done")
            time.sleep(2)  # Wait for stabilization

            # Perform measurement here
            # [INSERT CODE FOR MEASUREMENT]

        # Stop polling loop and disconnect devices before program finishes.
        device1.StopPolling()
        device2.StopPolling()
        device1.Disconnect()
        device2.Disconnect()

        restart = input("\nDo you want to restart the program? [y/n] > ")
        if restart == "y":
            os.execl(sys.executable, os.path.abspath(__file__), *sys.argv)
        else:
            print("\nThe program will be closed...")
            sys.exit(0)

    except Exception as e:
        print(e)
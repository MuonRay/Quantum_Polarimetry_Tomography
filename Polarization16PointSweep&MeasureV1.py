# -*- coding: utf-8 -*-
"""
Created on Tue Jan 30 11:48:39 2024

@author: ektop
"""

import os
import sys
import clr
import time

import ctypes
from ctypes import *
import csv
import numpy as np
import pandas as pd

# Load DLL library for polarization controllers
clr.AddReference("C:\\Program Files\\Thorlabs\\Kinesis\\Thorlabs.MotionControl.DeviceManagerCLI.dll")
clr.AddReference("C:\\Program Files\\Thorlabs\\Kinesis\\Thorlabs.MotionControl.GenericMotorCLI.dll")
clr.AddReference("C:\\Program Files\\Thorlabs\\Kinesis\\ThorLabs.MotionControl.PolarizerCLI.dll")
# Load DLL library for PAX1000
lib = cdll.LoadLibrary("C:\Program Files\IVI Foundation\VISA\Win64\Bin\TLPAX_64.dll")

from Thorlabs.MotionControl.DeviceManagerCLI import *
from Thorlabs.MotionControl.GenericMotorCLI import *
from Thorlabs.MotionControl.PolarizerCLI import *
from System import Decimal




# Detect and initialize PAX1000 devices

instrumentHandle1 = c_ulong()
instrumentHandle2 = c_ulong()
IDQuery = True
resetDevice = False
resource1 = c_char_p(b"")
resource2 = c_char_p(b"")
deviceCount = c_int()

# Check how many PAX1000 devices are connected
lib.TLPAX_findRsrc(instrumentHandle1, byref(deviceCount))
if deviceCount.value < 2:
    print("Not enough PAX1000 devices found.")
    exit()
else:
    print(deviceCount.value, "PAX1000 device(s) found.")
    print("")

# Connect to the first available PAX1000
lib.TLPAX_getRsrcName(instrumentHandle1, 0, resource1)
if (0 == lib.TLPAX_init(resource1.value, IDQuery, resetDevice, byref(instrumentHandle1))):
    print("Connection to first PAX1000 initialized.")
else:
    print("Error with initialization.")
    exit()
print("")

# Connect to the second available PAX1000
lib.TLPAX_getRsrcName(instrumentHandle2, 1, resource2)
if (0 == lib.TLPAX_init(resource2.value, IDQuery, resetDevice, byref(instrumentHandle2))):
    print("Connection to second PAX1000 initialized.")
else:
    print("Error with initialization.")
    exit()
print("")

# Short break to make sure the devices are correctly initialized
time.sleep(2)

# Make settings for the first PAX1000
lib.TLPAX_setMeasurementMode(instrumentHandle1, 9)
lib.TLPAX_setWavelength(instrumentHandle1, c_double(810e-9))
lib.TLPAX_setBasicScanRate(instrumentHandle1, c_double(60))

# Make settings for the second PAX1000
lib.TLPAX_setMeasurementMode(instrumentHandle2, 9)
lib.TLPAX_setWavelength(instrumentHandle2, c_double(810e-9))
lib.TLPAX_setBasicScanRate(instrumentHandle2, c_double(60))

# Check settings for the first PAX1000
wavelength1 = c_double()
lib.TLPAX_getWavelength(instrumentHandle1, byref(wavelength1))
print("Set wavelength for first PAX1000 [nm]: ", wavelength1.value * 1e9)
mode1 = c_int()
lib.TLPAX_getMeasurementMode(instrumentHandle1, byref(mode1))
print("Set mode for first PAX1000: ", mode1.value)
scanrate1 = c_double()
lib.TLPAX_getBasicScanRate(instrumentHandle1, byref(scanrate1))
print("Set scanrate for first PAX1000: ", scanrate1.value)
print("")

# Check settings for the second PAX1000
wavelength2 = c_double()
lib.TLPAX_getWavelength(instrumentHandle2, byref(wavelength2))
print("Set wavelength for second PAX1000 [nm]: ", wavelength2.value * 1e9)
mode2 = c_int()
lib.TLPAX_getMeasurementMode(instrumentHandle2, byref(mode2))
print("Set mode for second PAX1000: ", mode2.value)
scanrate2 = c_double()
lib.TLPAX_getBasicScanRate(instrumentHandle2, byref(scanrate2))
print("Set scanrate for second PAX1000: ", scanrate2.value)
print("")

# Short break
time.sleep(5)

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
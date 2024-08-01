# -*- coding: utf-8 -*-
"""
Created on Tue Jan 30 11:48:39 2024

@author: ektop
"""

import os
import sys
import clr
import time
from ctypes import *
import numpy as np

# Load DLL library for polarization controllers
clr.AddReference("C:\\Program Files\\Thorlabs\\Kinesis\\Thorlabs.MotionControl.DeviceManagerCLI.dll")
clr.AddReference("C:\\Program Files\\Thorlabs\\Kinesis\\Thorlabs.MotionControl.GenericMotorCLI.dll")
clr.AddReference("C:\\Program Files\\Thorlabs\\Kinesis\\ThorLabs.MotionControl.PolarizerCLI.dll")

# Load DLL library for PAX1000
lib = cdll.LoadLibrary("C:\\Program Files\\IVI Foundation\\VISA\\Win64\\Bin\\TLPAX_64.dll")

from Thorlabs.MotionControl.DeviceManagerCLI import *
from Thorlabs.MotionControl.PolarizerCLI import *
from System import Decimal

# Detect and initialize PAX1000 devices
def initialize_pax_device(handle_id):
    instrument_handle = c_ulong()
    resource = c_char_p(b"")
    ID_query = True
    reset_device = False

    lib.TLPAX_findRsrc(instrument_handle, byref(c_int()))
    lib.TLPAX_getRsrcName(instrument_handle, handle_id, resource)
    
    result = lib.TLPAX_init(resource.value, ID_query, reset_device, byref(instrument_handle))
    if result != 0:
        raise Exception(f"Error initializing PAX device # {handle_id}")
    
    return instrument_handle

try:
    instrument_handle1 = initialize_pax_device(0)
    print("Connection to first PAX1000 initialized.")
    
    instrument_handle2 = initialize_pax_device(1)
    print("Connection to second PAX1000 initialized.")

    time.sleep(2)

    # Setting up both PAX1000s
    for handle in (instrument_handle1, instrument_handle2):
        lib.TLPAX_setMeasurementMode(handle, 9)
        lib.TLPAX_setWavelength(handle, c_double(810e-9))
        lib.TLPAX_setBasicScanRate(handle, c_double(60))

    # Confirm settings
    for i, handle in enumerate((instrument_handle1, instrument_handle2), start=1):
        wavelength = c_double()
        lib.TLPAX_getWavelength(handle, byref(wavelength))
        print(f"Set wavelength for PAX1000 #{i} [nm]: {wavelength.value * 1e9}")

    time.sleep(5)

    measurement_angles = [
        Decimal(0.0), Decimal(45.0), Decimal(90.0), Decimal(135.0),
        Decimal(180.0), Decimal(225.0), Decimal(270.0), Decimal(315.0),
        Decimal(0.0), Decimal(45.0), Decimal(90.0), Decimal(135.0),
        Decimal(180.0), Decimal(225.0), Decimal(270.0), Decimal(315.0)
    ]

    RUN = True

    while RUN:
        try:
            # Build device list.
            DeviceManagerCLI.BuildDeviceList()

            # Create and connect polarization controllers
            device1 = Polarizer.CreatePolarizer("38390544")
            device2 = Polarizer.CreatePolarizer("38392094")
            device1.Connect("38390544")
            device2.Connect("38392094")

            # Wait for settings to initialize
            for device in (device1, device2):
                assert device.IsSettingsInitialized(), "Device settings not initialized"
                device.StartPolling(250)
                device.EnableDevice()
                time.sleep(0.25)

            # Get device info and display
            print(device1.GetDeviceInfo().Description)
            print(device2.GetDeviceInfo().Description)

            # Measurement loop
            for angle in measurement_angles:
                print(f"Moving both devices to {angle} degrees")
                device1.MoveTo(angle, PolarizerPaddles.Paddle1, 60000)
                device2.MoveTo(angle, PolarizerPaddles.Paddle1, 60000)
                print("Movement done. Waiting for stabilization...")
                time.sleep(2)  # Allow stabilization time

                # Perform simultaneous measurements from both polarimeters
                measurement1 = lib.TLPAX_measure(instrument_handle1)  # Hypothetical function for measurement
                measurement2 = lib.TLPAX_measure(instrument_handle2)
                print(f"Measurements at {angle} degrees: PAX1 = {measurement1}, PAX2 = {measurement2}")

            device1.StopPolling()
            device2.StopPolling()
            device1.Disconnect()
            device2.Disconnect()

            if input("\nDo you want to restart the program? [y/n] > ").lower() == "y":
                os.execl(sys.executable, os.path.abspath(__file__), *sys.argv)
            else:
                print("\nThe program will be closed...")
                sys.exit(0)

        except Exception as e:
            print("An error occurred:", e)

finally:
    # If anything goes wrong, ensure devices are disconnected properly
    try:
        # Disconnect PAX devices
        lib.TLPAX_close(instrument_handle1)
        lib.TLPAX_close(instrument_handle2)
    except Exception as ex:
        print("Error disconnecting devices:", ex)

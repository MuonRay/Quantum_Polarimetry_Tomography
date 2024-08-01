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
from decimal import Decimal

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

    # Define the wavelength range +/- 10 nm around 810 nm
    center_wavelength_nm = 810.0
    wavelength_range = np.arange(center_wavelength_nm - 10, center_wavelength_nm + 11, 1)  # 1 nm steps
    
    # Setting up both PAX1000s
    for handle in (instrument_handle1, instrument_handle2):
        lib.TLPAX_setMeasurementMode(handle, 9)  # Set measurement mode
        lib.TLPAX_setBasicScanRate(handle, c_double(60))  # Set basic scan rate

    # Confirm settings
    for i, handle in enumerate((instrument_handle1, instrument_handle2), start=1):
        print(f"Settings initialized for PAX1000 #{i}")

    time.sleep(5)

    measurement_angles = [
        Decimal(0.0), Decimal(45.0), Decimal(90.0), Decimal(135.0),
        Decimal(180.0), Decimal(225.0), Decimal(270.0), Decimal(315.0)
    ]

    RUN = True

    while RUN:
        try:
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

            # Measurement loop over each wavelength in the defined range
            for wavelength_nm in wavelength_range:
                wavelength_m = wavelength_nm * 1e-9  # Convert to meters
                for handle in (instrument_handle1, instrument_handle2):
                    lib.TLPAX_setWavelength(handle, c_double(wavelength_m))

                print(f"Measuring at wavelength: {wavelength_nm} nm")

                for angle in measurement_angles:
                    print(f"Moving both devices to {angle} degrees")
                    device1.MoveTo(angle, PolarizerPaddles.Paddle1, 60000)
                    device2.MoveTo(angle, PolarizerPaddles.Paddle1, 60000)
                    print("Movement done. Waiting for stabilization...")
                    time.sleep(2)  # Allow stabilization time

                    # Perform measurements from both polarimeters
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
    # Ensure devices are disconnected properly
    try:
        lib.TLPAX_close(instrument_handle1)
        lib.TLPAX_close(instrument_handle2)
    except Exception as ex:
        print("Error disconnecting devices:", ex)

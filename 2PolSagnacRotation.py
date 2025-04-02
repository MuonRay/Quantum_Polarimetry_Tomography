# -*- coding: utf-8 -*-
"""
Created on Tue Jan  7 15:33:12 2025

@author: ektop
"""

import os
import time
import ctypes
from ctypes import *
import csv
import numpy as np
import matplotlib.pyplot as plt

# Load DLL library
lib = cdll.LoadLibrary("C:\Program Files\IVI Foundation\VISA\Win64\Bin\TLPAX_64.dll")

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

# Make settings for the first PAX1000
lib.TLPAX_setMeasurementMode(instrumentHandle1, 9)
lib.TLPAX_setWavelength(instrumentHandle1, c_double(810e-9))
lib.TLPAX_setBasicScanRate(instrumentHandle1, c_double(60))

# Make settings for the second PAX1000
lib.TLPAX_setMeasurementMode(instrumentHandle2, 9)
lib.TLPAX_setWavelength(instrumentHandle2, c_double(810e-9))
lib.TLPAX_setBasicScanRate(instrumentHandle2, c_double(60))

# Short break to ensure devices are initialized
time.sleep(2)

# Prepare for real-time plotting
plt.ion()  # Turn on interactive mode
fig, ax = plt.subplots()
rotation_rates = []
time_stamps = []

# Continuous measurement loop
try:
    while True:
        # Retrieve measurements from the first PAX1000
        scanID1 = c_int()
        lib.TLPAX_getLatestScan(instrumentHandle1, byref(scanID1))
        
        azimuth1 = c_double()
        ellipticity1 = c_double()
        lib.TLPAX_getPolarization(instrumentHandle1, scanID1.value, byref(azimuth1), byref(ellipticity1))

        # Retrieve measurements from the second PAX1000
        scanID2 = c_int()
        lib.TLPAX_getLatestScan(instrumentHandle2, byref(scanID2))
        
        azimuth2 = c_double()
        ellipticity2 = c_double()
        lib.TLPAX_getPolarization(instrumentHandle2, scanID2.value, byref(azimuth2), byref(ellipticity2))

        # Calculate Stokes parameters
        S0_1 = np.cos(azimuth1.value)**2 + np.sin(azimuth1.value)**2 * np.cos(ellipticity1.value)**2
        S1_1 = np.cos(azimuth1.value)**2 - np.sin(azimuth1.value)**2 * np.cos(ellipticity1.value)**2
        
        S0_2 = np.cos(azimuth2.value)**2 + np.sin(azimuth2.value)**2 * np.cos(ellipticity2.value)**2
        S1_2 = np.cos(azimuth2.value)**2 - np.sin(azimuth2.value)**2 * np.cos(ellipticity2.value)**2
        
        # Calculate rotation rates
        k = 1  # Set a constant for k as per your requirement
        rotation_rate1 = S0_1 * np.arctan(k * (S1_1 / S0_1))
        rotation_rate2 = S0_2 * np.arctan(k * (S1_2 / S0_2))

        # Append values for plotting
        rotation_rates.append((rotation_rate1, rotation_rate2))
        time_stamps.append(time.time())

        # Update plot
        ax.clear()
        ax.plot(time_stamps, [rate[0] for rate in rotation_rates], label='Rotation Rate 1')
        ax.plot(time_stamps, [rate[1] for rate in rotation_rates], label='Rotation Rate 2')
        ax.legend()
        ax.set_xlabel('Time [s]')
        ax.set_ylabel('Rotation Rate [units]')
        plt.pause(0.1)  # Pause for a short interval to update the plot

        # Release scans
        lib.TLPAX_releaseScan(instrumentHandle1, scanID1)
        lib.TLPAX_releaseScan(instrumentHandle2, scanID2)

except KeyboardInterrupt:
    print("Measurement stopped by user.")

# Close connections
lib.TLPAX_close(instrumentHandle1)
lib.TLPAX_close(instrumentHandle2)
print("Connections to PAX1000 devices closed.")

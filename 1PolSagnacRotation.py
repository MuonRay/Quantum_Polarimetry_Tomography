
# -*- coding: utf-8 -*-
"""
Created on Tue Jan  7 15:43:47 2025

@author: ektop
"""

import os
import time
import ctypes
from ctypes import *
import numpy as np
import matplotlib.pyplot as plt
import signal

# Load DLL library
lib = cdll.LoadLibrary("C:\\Program Files\\IVI Foundation\\VISA\\Win64\\Bin\\TLPAX_64.dll")

# Detect and initialize PAX1000 device
instrumentHandle = c_ulong()
IDQuery = True
resetDevice = False
resource = c_char_p(b"")
deviceCount = c_int()

# Check how many PAX1000 devices are connected
lib.TLPAX_findRsrc(instrumentHandle, byref(deviceCount))
if deviceCount.value < 1:
    print("No PAX1000 devices found.")
    exit()
else:
    print(deviceCount.value, "PAX1000 device(s) found.")
    print("")

# Connect to the first available PAX1000
lib.TLPAX_getRsrcName(instrumentHandle, 0, resource)
if (0 == lib.TLPAX_init(resource.value, IDQuery, resetDevice, byref(instrumentHandle))):
    print("Connection to PAX1000 initialized.")
else:
    print("Error with initialization.")
    exit()
print("")

# Make settings for the PAX1000
lib.TLPAX_setMeasurementMode(instrumentHandle, 9)
lib.TLPAX_setWavelength(instrumentHandle, c_double(810e-9))
lib.TLPAX_setBasicScanRate(instrumentHandle, c_double(60))

# Short break to ensure device is initialized
time.sleep(2)

# Prepare for real-time plotting
plt.ion()  # Turn on interactive mode
fig, ax = plt.subplots()
rotation_rates = []
S1_values = []
time_stamps = []

# Function to handle interrupt and save the plot
def handle_interrupt(signal, frame):
    ax.clear()
    ax.plot(time_stamps, rotation_rates, label='Rotation Rate', color='blue')
    ax.plot(time_stamps, S1_values, label='S1', color='orange')
    ax.legend()
    ax.set_xlabel('Time [s]')
    ax.set_ylabel('Values')
    ax.set_title('Real-Time Data of S1 and Rotation Rate')

    # Generate a unique filename based on the current timestamp
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    filename = f"plot_{timestamp}.png"
    
    plt.savefig(filename)  # Save the plot to a PNG file
    plt.show()
    exit(0)

signal.signal(signal.SIGINT, handle_interrupt)

# Continuous measurement loop
try:
    while True:
        # Retrieve measurements from the PAX1000
        scanID = c_int()
        lib.TLPAX_getLatestScan(instrumentHandle, byref(scanID))
        
        azimuth = c_double()
        ellipticity = c_double()
        lib.TLPAX_getPolarization(instrumentHandle, scanID.value, byref(azimuth), byref(ellipticity))


        power = c_double()
        powerPolarized = c_double()
        powerUnpolarized = c_double()
        lib.TLPAX_getPower(instrumentHandle, scanID.value, byref(power), byref(powerPolarized), byref(powerUnpolarized))
        # Calculate Stokes parameters
        
        #s1 = c_double()
        #s2 = c_double()
        #s3 = c_double()
        #lib.TLPAX_getStokes(instrumentHandle, scanID.value, byref(s1), byref(s2), byref(s3))
        
        
        S0 = powerPolarized
        #S1 = s1
        S1 = np.cos(azimuth) * np.cos(ellipticity)
        
        # Calculate rotation rate
        k = 1  # Set a constant for k as per your requirement
        rotation_rate = S0 * np.arctan(k * (S1 / S0))

        # Append values for plotting
        rotation_rates.append(rotation_rate)
        S1_values.append(S1)
        time_stamps.append(time.time())

        # Update plot
        ax.clear()
        ax.plot(time_stamps, rotation_rates, label='Rotation Rate', color='blue')
        ax.plot(time_stamps, S1_values, label='S1', color='orange')
        ax.legend()
        ax.set_xlabel('Time [s]')
        ax.set_ylabel('Values')
        ax.set_title('Real-Time Data of S1 and Rotation Rate')
        plt.pause(0.1)  # Pause for a short interval to update the plot

        # Release scan
        lib.TLPAX_releaseScan(instrumentHandle, scanID)

except KeyboardInterrupt:
    handle_interrupt(None, None)

# Close connections
lib.TLPAX_close(instrumentHandle)
print("Connection to PAX1000 device closed.")

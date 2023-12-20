# -*- coding: utf-8 -*-
"""
Created on Wed Nov 22 16:08:56 2023
2 PAX1000 connection with polarization azimuth and ellipse for stokes vector calculation 
@author: ektop
"""

import os
import time
import ctypes
from ctypes import *
import csv

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

# Take 5 measurements on the first PAX1000 and output values to a csv file
filename1 = "pax1000_1_measurements.csv"
with open(filename1, "w", newline="") as file:
    writer = csv.writer(file)
    writer.writerow(["Measurement", "Azimuth [rad]", "Ellipticity [rad]"])
    
    for x in range(5):
        revolutionCounter = c_int()
        scanID = c_int()
        lib.TLPAX_getLatestScan(instrumentHandle1, byref(scanID))
    
        azimuth = c_double()
        ellipticity = c_double()
        lib.TLPAX_getPolarization(instrumentHandle1, scanID.value, byref(azimuth), byref(ellipticity))
        
        writer.writerow([x+1, azimuth.value, ellipticity.value])
        
        lib.TLPAX_releaseScan(instrumentHandle1, scanID)
        time.sleep(0.5)

# Take 5 measurements on the second PAX1000 and output values to a csv file
filename2 = "pax1000_2_measurements.csv"
with open(filename2, "w", newline="") as file:
    writer = csv.writer(file)
    writer.writerow(["Measurement", "Azimuth [rad]", "Ellipticity [rad]"])
    
    for x in range(5):
        revolutionCounter = c_int()
        scanID = c_int()
        lib.TLPAX_getLatestScan(instrumentHandle2, byref(scanID))
    
        azimuth = c_double()
        ellipticity = c_double()
        lib.TLPAX_getPolarization(instrumentHandle2, scanID.value, byref(azimuth), byref(ellipticity))
        
        writer.writerow([x+1, azimuth.value, ellipticity.value])
        
        lib.TLPAX_releaseScan(instrumentHandle2, scanID)
        time.sleep(0.5)

# Close connections
lib.TLPAX_close(instrumentHandle1)
lib.TLPAX_close(instrumentHandle2)
print("Connections to PAX1000 devices closed.")
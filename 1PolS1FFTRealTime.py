import os
import time
import ctypes
from ctypes import *
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import butter, filtfilt
import cv2

import warnings
warnings.filterwarnings("ignore")



start_time = time.time()

def handle_interrupt(signal, frame):
    plt.plot(time_stamps, rotation_rates)
    plt.xlabel('Time (seconds)')
    plt.ylabel('Omega (Rotation Rate)')
    plt.title('Omega vs Time')
    
    # Generate a unique filename based on the current timestamp
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    filename = f"plot_{timestamp}.png"
    
    plt.savefig(filename)  # Save the plot to a PNG file
    plt.show()
    exit(0)
    
    
# Load DLL library
lib = cdll.LoadLibrary("C:\\Program Files\\IVI Foundation\\VISA\\Win64\\Bin\\TLPAX_64.dll")

# Detect and initialize PAX1000 device
instrumentHandle = c_ulong()
IDQuery = True
resetDevice = False
resource = c_char_p(b"")
deviceCount = c_int()

# Prepare for real-time plotting
plt.ion()  # Turn on interactive mode
rotation_rates = []
S0_values = []
S1_values = []
time_stamps = []

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

# Short break to make sure the device is correctly initialized
time.sleep(2)

# Make settings for the PAX1000
lib.TLPAX_setMeasurementMode(instrumentHandle, 9)
lib.TLPAX_setWavelength(instrumentHandle, c_double(810e-9))
lib.TLPAX_setBasicScanRate(instrumentHandle, c_double(60))

# Check settings for the PAX1000
wavelength = c_double()
lib.TLPAX_getWavelength(instrumentHandle, byref(wavelength))
print("Set wavelength for PAX1000 [nm]: ", wavelength.value * 1e9)
mode = c_int()
lib.TLPAX_getMeasurementMode(instrumentHandle, byref(mode))
print("Set mode for PAX1000: ", mode.value)
scanrate = c_double()
lib.TLPAX_getBasicScanRate(instrumentHandle, byref(scanrate))
print("Set scanrate for PAX1000: ", scanrate.value)
print("")

# Short break
time.sleep(5)

try:
    while True:
        scanID = c_int()
        lib.TLPAX_getLatestScan(instrumentHandle, byref(scanID))

        timeStamp = round(time.time() * 1000)
        upTime = c_int()
        timePola = lib.TLPAX_getTimeStamp(instrumentHandle, scanID.value, byref(upTime))
        diff = timeStamp - int(upTime.value)
        
        power = c_double()
        powerPolarized = c_double()
        powerUnpolarized = c_double()
        lib.TLPAX_getPower(instrumentHandle, scanID.value, byref(power), byref(powerPolarized), byref(powerUnpolarized))
        
        #polarization degrees, dop, dolp (degree of linear polarization) and docp (degree of circular polarization)
        dop = c_double()
        dolp = c_double()
        docp = c_double()
        lib.TLPAX_getDOP(instrumentHandle, scanID.value, byref(dop), byref(dolp), byref(docp))

        azimuth = c_double()
        ellipticity = c_double()
        lib.TLPAX_getPolarization(instrumentHandle, scanID.value, byref(azimuth), byref(ellipticity))

        S1 = np.cos(ellipticity.value) * np.cos(azimuth.value)
        S0 = power
        #new polarization quantities
        DeltaPolDegree = docp - dolp
        PolDegreeRatio = docp/dolp
        print(f"S0 = {S0.value}, S1 = {S1}")

        lib.TLPAX_releaseScan(instrumentHandle, scanID)
        time.sleep(0.5)  # Adjust sampling rate as needed
        
        # Calculate rotation rate
        k = 1  # Set a constant for k as per your requirement
        rotation_rate = S0.value * np.arctan(k * (S1 / S0.value))
        print(f"Omega = {rotation_rate}")

        # Append values for plotting
        rotation_rates.append(rotation_rate)
        S1_values.append(S1)
        S0_values.append(S0.value)

        time_stamps.append(time.time())

except KeyboardInterrupt:
    print("Measurement stopped by user.")
    
    plt.plot(time_stamps, rotation_rates)
    plt.xlabel('Time (seconds)')
    plt.ylabel('Omega (Rotation Rate)')
    plt.title('Omega vs Time')
    
    # Generate a unique filename based on the current timestamp
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    filename = f"plot_{timestamp}.png"
    
    plt.savefig(filename)  # Save the plot to a PNG file
    plt.show()


# Close connection
lib.TLPAX_close(instrumentHandle)
print("Connection to PAX1000 device closed.")

# Plot S1 values
plt.figure()
plt.plot(time_stamps, S1_values, label='S1', color='orange')
plt.xlabel('Time [s]')
plt.ylabel('S1 Values')
plt.title('S1 Data Over Time')
plt.legend()
plt.grid()
plt.show()

# Plot Rotation Rates (Omega)
plt.figure()
plt.plot(time_stamps, rotation_rates, label='Rotation Rate', color='blue')
plt.xlabel('Time [s]')
plt.ylabel('Rotation Rate (Omega)')
plt.title('Rotation Rate Data Over Time')
plt.legend()
plt.grid()
plt.show()





# Example Omega values and time stamps
Omega_values = np.array(rotation_rates)
time_stamps = np.array(time_stamps)  # Ensure this is defined

# FFT Calculation
fft_result = np.fft.fft(Omega_values)
fft_freq = np.fft.fftfreq(len(Omega_values), d=(time_stamps[1] - time_stamps[0]))  # Sampling interval

# # Option: High Pass Filter
apply_high_pass_filter = True  # Set to True to apply filter, False to skip
high_cutoff_freq = 0.5  # Cutoff frequency for high-pass filter in Hz

if apply_high_pass_filter:
    # Butterworth High Pass Filter
    def butter_highpass(cutoff, fs, order=5):
        nyquist = 0.5 * fs
        normal_cutoff = cutoff / nyquist
        b, a = butter(order, normal_cutoff, btype='high', analog=False)
        return b, a

    def highpass_filter(data, cutoff, fs, order=5):
        b, a = butter_highpass(cutoff, fs, order=order)
        y = filtfilt(b, a, data)
        return y

    filtered_Omega_values = highpass_filter(Omega_values, high_cutoff_freq, 1/(time_stamps[1] - time_stamps[0]))

# # Option: Low Pass Filter
apply_low_pass_filter = False  # Set to True to apply filter, False to skip
low_cutoff_freq = 2.0  # Cutoff frequency for low-pass filter in Hz

if apply_low_pass_filter:
    # Butterworth Low Pass Filter
    def butter_lowpass(cutoff, fs, order=5):
        nyquist = 0.5 * fs
        normal_cutoff = cutoff / nyquist
        b, a = butter(order, normal_cutoff, btype='low', analog=False)
        return b, a

    def lowpass_filter(data, cutoff, fs, order=5):
        b, a = butter_lowpass(cutoff, fs, order=order)
        y = filtfilt(b, a, data)
        return y

    filtered_Omega_values = lowpass_filter(Omega_values, low_cutoff_freq, 1/(time_stamps[1] - time_stamps[0]))

# Use filtered data for FFT if filtering was applied
if apply_high_pass_filter or apply_low_pass_filter:
    Omega_values = filtered_Omega_values

# Plot FFT
plt.figure()
plt.plot(fft_freq[:len(fft_freq)//2], np.abs(np.fft.fft(Omega_values))[:len(fft_result)//2])
plt.title('FFT of Omega Data')
plt.xlabel('Frequency [Hz]')
plt.ylabel('Magnitude')
plt.grid()
plt.show()



cv2.destroyAllWindows()





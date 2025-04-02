# -*- coding: utf-8 -*-
"""
Created on Tue Jan  7 16:57:10 2025

@author: ektop
"""

import serial
import time
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

# Configure the serial connection to the PAX1000
serial_port = 'COM3'  # Change this to your PAX1000 port (e.g., '/dev/ttyUSB0' on Linux)
baud_rate = 9600

# Initialize the serial connection
ser = serial.Serial(serial_port, baud_rate, timeout=1)

# Lists to store S1 and S0 values
S1_values = []
S0_values = []

# Function to read data from the PAX1000
def read_data():
    ser.write(b'YOUR_COMMAND_TO_GET_DATA
')  # Replace with the actual command to get S1 and S0
    response = ser.readline().decode('utf-8').strip()
    try:
        S0, S1 = map(float, response.split(','))  # Assuming the response is 'S0,S1'
        return S0, S1
    except ValueError:
        return None, None

# Function to update the plot
def update(frame):
    S0, S1 = read_data()
    if S0 is not None and S1 is not None:
        S0_values.append(S0)
        S1_values.append(S1)

        # Limit the x-axis to the last 100 readings
        if len(S0_values) > 100:
            S0_values.pop(0)
            S1_values.pop(0)

        ax.clear()
        ax.plot(S0_values, label='S0', color='blue')
        ax.plot(S1_values, label='S1', color='orange')
        ax.set_title('Real-Time S0 and S1 Values')
        ax.set_xlabel('Time (samples)')
        ax.set_ylabel('Values')
        ax.legend()
        ax.grid()

# Set up the plot
fig, ax = plt.subplots()
ani = FuncAnimation(fig, update, interval=100)  # Update every 100 ms
plt.show()

# Close the serial connection when done
ser.close()
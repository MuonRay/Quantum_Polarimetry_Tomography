# -*- coding: utf-8 -*-
"""
Created on Sun Dec 10 18:52:07 2023

@author: ektop
"""

import numpy as np
import csv
from qutip import Qobj, wigner

# Step 1: Read the PER measurements from the CSV files
with open("PER1.csv", "r") as file:
    reader = csv.reader(file)
    next(reader)  # Skip the header row
    PER1_data = np.array([float(row[1]) for row in reader])

with open("PER2.csv", "r") as file:
    reader = csv.reader(file)
    next(reader)  # Skip the header row
    PER2_data = np.array([float(row[1]) for row in reader])

# Step 2: Construct a random measurement matrix M
M = np.random.rand(5, 5) + 1j * np.random.rand(5, 5)

# Step 3: Solve the linear equation M * x = y to obtain the estimated density matrix
x = np.linalg.lstsq(M, np.concatenate((PER1_data, PER2_data)), rcond=None)[0]

# Step 4: Create the density matrix from the estimated elements
rho = Qobj(np.reshape(x, (4, 4)))

# Step 5: Calculate the Wigner function
num_points = 100
x = np.linspace(-5, 5, num_points)
p = np.linspace(-5, 5, num_points)
W = wigner(rho, x, p)

# Display the Wigner function
import matplotlib.pyplot as plt
plt.contourf(x, p, W, levels=100)
plt.xlabel('x')
plt.ylabel('p')
plt.title('Wigner function')
plt.colorbar()
plt.show()
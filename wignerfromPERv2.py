# -*- coding: utf-8 -*-
"""
Created on Sun Dec 10 18:53:35 2023

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

# Step 2: Construct a random measurement matrix M with 5 rows
M = np.random.rand(5, 16) + 1j * np.random.rand(5, 16)

# Step 3: Solve the linear equation M * x = y to obtain the estimated density matrix
M_pinv = np.linalg.pinv(M)  # Calculate pseudo-inverse of M
x1 = np.dot(M_pinv, PER1_data[:5])
x2 = np.dot(M_pinv, PER2_data[:5])
x = np.concatenate((x1, x2))

# Step 4: Create the density matrix from the estimated elements
if len(x) == 16:
    rho = Qobj(np.reshape(x, (4, 4)))
elif len(x) == 32:
    rho = Qobj(np.reshape(x[:16], (4, 4)))
else:
    print("Invalid size of array x. Unable to create density matrix.")
    exit(1)

# Step 5: Calculate the Wigner function
if len(x) == 16:
    W = wigner(rho, x, p)
elif len(x) == 32:
    W = wigner(rho, x[16:], p)
else:
    print("Invalid size of array x. Unable to calculate Wigner function.")
    exit(1)
    
# Step 6: Plot the Wigner function
plt.contourf(x, p, W, levels=100)
plt.xlabel('q')
plt.ylabel('p')
plt.title('Wigner function')
plt.colorbar()
plt.show()
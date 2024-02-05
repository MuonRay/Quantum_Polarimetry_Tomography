# -*- coding: utf-8 -*-
"""
Created on Mon Feb  5 15:11:32 2024

@author: ektop
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from qutip import *

# Load the Pauli matrices from CSV files
pauli_matrices1 = []
pauli_matrices2 = []

df1 = pd.read_csv('pax1000_1_measurement1.csv', header=None)
pauli_matrices1.append(df1.values)

df2 = pd.read_csv('pax1000_2_measurement1.csv', header=None)
pauli_matrices2.append(df2.values)

# Define the Pauli operators
sigma0 = qeye(2)
sigma1 = sigmax()
sigma2 = sigmay()
sigma3 = sigmaz()

# Create the density matrix from the Pauli matrices
rho1 = (pauli_matrices1[0][0][0] * sigma0 + pauli_matrices1[0][0][1] * sigma1 +
        pauli_matrices1[0][1][0] * sigma2 + pauli_matrices1[0][1][1] * sigma3) / 2

rho2 = (pauli_matrices2[0][0][0] * sigma0 + pauli_matrices2[0][0][1] * sigma1 +
        pauli_matrices2[0][1][0] * sigma2 + pauli_matrices2[0][1][1] * sigma3) / 2

# Create the Hinton plot
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 5))

hinton(rho1, ax=ax1)
ax1.set_title('Density Matrix - PAX1000 1 - Measurement 1')

hinton(rho2, ax=ax2)
ax2.set_title('Density Matrix - PAX1000 2 - Measurement 1')

plt.show()
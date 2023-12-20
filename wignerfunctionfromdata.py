




import numpy as np
from qutip import Qobj, basis, ket2dm, QobjEvo, mesolve, qeye, expect, wigner

# Step 3: Obtain measurement statistics (example data)
measurement_data = np.array([0.75, 0.25, 0.5, -0.25, 0.6, 0.1, -0.3, 0.4, 0.2, -0.1, 0.3, -0.2, 0.7, -0.4, -0.6, 0.5])

# Step 4: Reconstruct the density matrix
rho = np.zeros((4, 4), dtype=np.complex128)
rho[0, 0] = (measurement_data[0] + measurement_data[1]) / 2
rho[1, 1] = (measurement_data[0] - measurement_data[1]) / 2
rho[2, 2] = (measurement_data[0] + measurement_data[2]) / 2
rho[3, 3] = (measurement_data[0] - measurement_data[2]) / 2
rho[0, 1] = rho[1, 0] = (measurement_data[3] + 1j * measurement_data[2]) / 2
rho[0, 2] = rho[2, 0] = (measurement_data[3] + 1j * measurement_data[1]) / 2
rho[1, 2] = rho[2, 1] = (measurement_data[3] + 1j * measurement_data[0]) / 2

rho = Qobj(rho)

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
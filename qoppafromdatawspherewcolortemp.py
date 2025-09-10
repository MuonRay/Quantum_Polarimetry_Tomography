# -*- coding: utf-8 -*-
"""
Created on Tue Sep  9 16:19:17 2025

@author: ektop
"""

# -*- coding: utf-8 -*-
"""
Created on Tue Sep  9 15:38:41 2025

@author: ektop
"""

# -*- coding: utf-8 -*-
"""
Created on Tue Sep  9 15:17:40 2025
@author: ektop

Estimate Qoppa_P from Thorlabs PAX1000 polarization data (Azimuth, Ellipticity)
and visualize polarization trajectory on the Poincaré sphere with Qoppa extrema.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
from mpl_toolkits.mplot3d import Axes3D  # Required for 3D plotting
import matplotlib.cm as cm
import matplotlib.colors as mcolors
# --- Core Functions ---

def azimuth_ellipticity_to_stokes(azimuth, ellipticity):
    S1 = np.cos(2 * azimuth) * np.cos(2 * ellipticity)
    S2 = np.sin(2 * azimuth) * np.cos(2 * ellipticity)
    S3 = np.sin(2 * ellipticity)
    return S1, S2, S3

def compute_polarization_shift_from_ellipse(azimuth, ellipticity):
    S1, S2, S3 = azimuth_ellipticity_to_stokes(azimuth, ellipticity)
    S = np.vstack([S1, S2, S3]).T
    S_unit = S / (np.linalg.norm(S, axis=1, keepdims=True) + 1e-12)
    dot_products = np.sum(S_unit[1:] * S_unit[:-1], axis=1)
    dot_products = np.clip(dot_products, -1.0, 1.0)
    delta_P = np.arccos(dot_products)
    return np.insert(delta_P, 0, 0)

def compute_action_derivative(energy_proxy, time):
    return np.gradient(energy_proxy, time)

def estimate_qoppa(delta_P, dSdt):
    epsilon = 1e-12
    return delta_P / (dSdt + epsilon)

def plot_qoppa_vs_time(time, qoppa):
    plt.figure(figsize=(12, 6))
    plt.plot(time, qoppa, label='Estimated Qoppa_P', color='purple')
    plt.xlabel('Time (s)')
    plt.ylabel('Qoppa_P')
    plt.title('Qoppa_P Estimated from Polarimeter Data')
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.show()

def plot_poincare_sphere(S1, S2, S3, qoppa, time):
    from mpl_toolkits.mplot3d import Axes3D

    max_idx = np.argmax(qoppa)
    min_idx = np.argmin(qoppa)

    fig = plt.figure(figsize=(12, 9))
    ax = fig.add_subplot(111, projection='3d')

    # === Poincaré sphere wireframe ===
    u, v = np.mgrid[0:2*np.pi:50j, 0:np.pi:25j]
    x = np.cos(u) * np.sin(v)
    y = np.sin(u) * np.sin(v)
    z = np.cos(v)
    ax.plot_wireframe(x, y, z, color='violet', alpha=0.2)

    # === Create color map for Qoppa ===
    norm = mcolors.Normalize(vmin=np.min(qoppa), vmax=np.max(qoppa))
    cmap = cm.plasma  # Or 'viridis', 'coolwarm', etc.

    # === Plot colored trajectory ===
    for i in range(len(S1) - 1):
        x_vals = [S1[i], S1[i+1]]
        y_vals = [S2[i], S2[i+1]]
        z_vals = [S3[i], S3[i+1]]
        color = cmap(norm(qoppa[i]))
        ax.plot(x_vals, y_vals, z_vals, color=color, linewidth=2)

    # === Add colorbar ===
    sm = cm.ScalarMappable(cmap=cmap, norm=norm)
    sm.set_array([])
    cbar = plt.colorbar(sm, pad=0.1, ax=ax, shrink=0.7)
    cbar.set_label('Qoppa_P Value', fontsize=12)

    # === Mark and annotate Max/Min Qoppa ===
    ax.scatter(S1[max_idx], S2[max_idx], S3[max_idx], color='yellow', s=80, label='Max Qoppa')
    ax.scatter(S1[min_idx], S2[min_idx], S3[min_idx], color='blue', s=80, label='Min Qoppa')
    ax.text(S1[max_idx], S2[max_idx], S3[max_idx], 'Max Qoppa', color='red', fontsize=10)
    ax.text(S1[min_idx], S2[min_idx], S3[min_idx], 'Min Qoppa', color='green', fontsize=10)

    # === Axes and formatting ===
    ax.set_xlabel('S1')
    ax.set_ylabel('S2')
    ax.set_zlabel('S3')
    ax.set_title('Qoppa-Colored Polarization Trajectory on Poincaré Sphere')
    ax.legend()

    # === Zoom settings ===
    zoom = 1
    ax.set_xlim([-zoom, zoom])
    ax.set_ylim([-zoom, zoom])
    ax.set_zlim([-zoom, zoom])

    # === Camera angle ===
    ax.view_init(elev=0, azim=40)  # Adjust for clarity

    # === Layout ===
    fig.subplots_adjust(left=0.1, right=0.88)
    plt.tight_layout(pad=0.3)
    plt.show()

def analyze_polarimeter_data_from_azimuth_ellipticity(filename, timestep=0.01):
    # Auto-detect delimiter (comma or tab)
    with open(filename, 'r', encoding='utf-8') as f:
        first_line = f.readline()
        delimiter = ',' if ',' in first_line else '\t'

    # Load data using detected delimiter
    df = pd.read_csv(filename, delimiter=delimiter)

    # Check for required columns
    expected_cols = ['Azimuth [rad]', 'Ellipticity [rad]']
    if not all(col in df.columns for col in expected_cols):
        raise ValueError(f"Expected columns: {expected_cols}. Found: {list(df.columns)}")

    azimuth = df['Azimuth [rad]'].values
    ellipticity = df['Ellipticity [rad]'].values
    time = np.arange(len(azimuth)) * timestep

    # ΔP(t)
    delta_P = compute_polarization_shift_from_ellipse(azimuth, ellipticity)

    # SOP & energy proxy
    S1, S2, S3 = azimuth_ellipticity_to_stokes(azimuth, ellipticity)
    energy_proxy = np.sqrt(S1**2 + S2**2 + S3**2)

    # dS/dt
    dSdt = compute_action_derivative(energy_proxy, time)

    # Qoppa
    qoppa = estimate_qoppa(delta_P, dSdt)

    # Plot results
    plot_qoppa_vs_time(time, qoppa)
    plot_poincare_sphere(S1, S2, S3, qoppa, time)

    # Save result
    output_df = pd.DataFrame({
        'Time (s)': time,
        'Azimuth [rad]': azimuth,
        'Ellipticity [rad]': ellipticity,
        'Delta_P (rad)': delta_P,
        'dS/dt': dSdt,
        'Qoppa_P': qoppa
    })

    out_file = os.path.splitext(filename)[0] + '_qoppa_output.csv'
    output_df.to_csv(out_file, index=False)
    print(f"\n✅ Results saved to: {out_file}")

    return time, qoppa, delta_P, dSdt

# --- Run Section ---
def main():
    # Change the filename below to match your actual file
    filename = "256BB0_pax1000_2_measurements.csv"
    timestep = 0.01  # seconds between measurements (adjust as needed)

    # Run analysis
    time, qoppa, delta_P, dSdt = analyze_polarimeter_data_from_azimuth_ellipticity(filename, timestep)

if __name__ == "__main__":
    main()

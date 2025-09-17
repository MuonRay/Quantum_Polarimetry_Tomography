# -*- coding: utf-8 -*-
"""
Created on Mon Sep 15 18:10:07 2025

@author: ektop
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
from mpl_toolkits.mplot3d import Axes3D  # Required for 3D plotting
import matplotlib.cm as cm
import matplotlib.colors as mcolors
from scipy.ndimage import uniform_filter1d
from sklearn.preprocessing import MinMaxScaler  # For normalization

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

def plot_qoppa_bounds_vs_time(time, qoppa, window_size=20):
    qoppa_smooth = uniform_filter1d(qoppa, size=window_size)
    rolling_std = uniform_filter1d(np.abs(qoppa - qoppa_smooth), size=window_size)

    upper_bound = qoppa_smooth + rolling_std
    lower_bound = qoppa_smooth - rolling_std

    plt.figure(figsize=(12, 6))
    plt.plot(time, qoppa, color='purple', label='Qoppa_P')
    plt.plot(time, upper_bound, color='red', linestyle='--', label='Upper Bound (Instability)')
    plt.plot(time, lower_bound, color='green', linestyle='--', label='Lower Bound (Stable Entanglement)')
    plt.fill_between(time, lower_bound, upper_bound, color='gray', alpha=0.2)

    plt.xlabel('Time (s)')
    plt.ylabel('Qoppa_P')
    plt.title('Qoppa_P with Upper and Lower Bound Indicators')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()

def plot_poincare_sphere(S1, S2, S3, qoppa, time):
    max_idx = np.argmax(qoppa)
    min_idx = np.argmin(qoppa)

    fig = plt.figure(figsize=(12, 9))
    ax = fig.add_subplot(111, projection='3d')

    u, v = np.mgrid[0:2*np.pi:50j, 0:np.pi:25j]
    x = np.cos(u) * np.sin(v)
    y = np.sin(u) * np.sin(v)
    z = np.cos(v)
    ax.plot_wireframe(x, y, z, color='violet', alpha=0.2)

    norm = mcolors.Normalize(vmin=np.min(qoppa), vmax=np.max(qoppa))
    cmap = cm.plasma

    for i in range(len(S1) - 1):
        x_vals = [S1[i], S1[i+1]]
        y_vals = [S2[i], S2[i+1]]
        z_vals = [S3[i], S3[i+1]]
        color = cmap(norm(qoppa[i]))
        ax.plot(x_vals, y_vals, z_vals, color=color, linewidth=2)

    sm = cm.ScalarMappable(cmap=cmap, norm=norm)
    sm.set_array([])
    cbar = plt.colorbar(sm, pad=0.1, ax=ax, shrink=0.7)
    cbar.set_label('Qoppa_P Value', fontsize=12)

    ax.scatter(S1[max_idx], S2[max_idx], S3[max_idx], color='yellow', s=80, label='Max Qoppa')
    ax.scatter(S1[min_idx], S2[min_idx], S3[min_idx], color='blue', s=80, label='Min Qoppa')
    ax.text(S1[max_idx], S2[max_idx], S3[max_idx], 'Max Qoppa', color='red', fontsize=10)
    ax.text(S1[min_idx], S2[min_idx], S3[min_idx], 'Min Qoppa', color='green', fontsize=10)

    ax.set_xlabel('S1')
    ax.set_ylabel('S2')
    ax.set_zlabel('S3')
    ax.set_title('Qoppa-Colored Polarization Trajectory on Poincaré Sphere')
    ax.legend()

    zoom = 1
    ax.set_xlim([-zoom, zoom])
    ax.set_ylim([-zoom, zoom])
    ax.set_zlim([-zoom, zoom])
    ax.view_init(elev=0, azim=40)

    fig.subplots_adjust(left=0.1, right=0.88)
    plt.tight_layout(pad=0.3)
    plt.show()

# --- New: Takens Embedding Functions ---

def takens_embedding(time_series, delay, dimension):
    """
    Constructs Takens embedding of a 1D time series.

    Args:
        time_series (np.ndarray): 1D array of the scalar time series.
        delay (int): Time delay τ in samples.
        dimension (int): Embedding dimension m.

    Returns:
        embedded (np.ndarray): Embedded trajectory of shape (N - (m-1)*τ, m)
    """
    N = len(time_series)
    if (dimension - 1) * delay >= N:
        raise ValueError("Time series too short for given embedding parameters.")

    embedded = np.array([
        time_series[i: N - (dimension - 1) * delay + i : delay]
        for i in range(dimension)
    ]).T

    return embedded

def plot_takens_embedding(embedded, title="Takens Embedding"):
    dim = embedded.shape[1]
    fig = plt.figure(figsize=(10, 8))
    if dim >= 3:
        ax = fig.add_subplot(111, projection='3d')
        ax.plot(embedded[:, 0], embedded[:, 1], embedded[:, 2], lw=1.2, color='darkorange')
        ax.set_xlabel('Qoppa(t)')
        ax.set_ylabel('Qoppa(t + τ)')
        ax.set_zlabel('Qoppa(t + 2τ)')
        ax.set_title(title)
    else:
        plt.plot(embedded[:, 0], embedded[:, 1], lw=1.2)
        plt.xlabel('Qoppa(t)')
        plt.ylabel(f'Qoppa(t + τ)')
        plt.title(title)
    plt.grid(True)
    plt.tight_layout()
    plt.show()

# --- Main Analysis Function ---

def analyze_polarimeter_data_from_azimuth_ellipticity(filename, timestep=0.01):
    with open(filename, 'r', encoding='utf-8') as f:
        first_line = f.readline()
        delimiter = ',' if ',' in first_line else '\t'

    df = pd.read_csv(filename, delimiter=delimiter)

    expected_cols = ['Azimuth [rad]', 'Ellipticity [rad]']
    if not all(col in df.columns for col in expected_cols):
        raise ValueError(f"Expected columns: {expected_cols}. Found: {list(df.columns)}")

    azimuth = df['Azimuth [rad]'].values
    ellipticity = df['Ellipticity [rad]'].values
    time = np.arange(len(azimuth)) * timestep

    delta_P = compute_polarization_shift_from_ellipse(azimuth, ellipticity)
    S1, S2, S3 = azimuth_ellipticity_to_stokes(azimuth, ellipticity)
    energy_proxy = np.sqrt(S1**2 + S2**2 + S3**2)
    dSdt = compute_action_derivative(energy_proxy, time)
    qoppa = estimate_qoppa(delta_P, dSdt)

    # Plots
    plot_qoppa_vs_time(time, qoppa)
    plot_qoppa_bounds_vs_time(time, qoppa)
    plot_poincare_sphere(S1, S2, S3, qoppa, time)

    # Save results
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

    # --- New: Takens Embedding on Qoppa_P ---

    embedding_delay = 10  # samples
    embedding_dim = 3     # dimensions

    scaler = MinMaxScaler()
    qoppa_scaled = scaler.fit_transform(qoppa.reshape(-1, 1)).flatten()

    qoppa_embedded = takens_embedding(qoppa_scaled, delay=embedding_delay, dimension=embedding_dim)

    plot_takens_embedding(qoppa_embedded, title="Takens Embedding of Qoppa_P")

    embed_out_file = os.path.splitext(filename)[0] + '_qoppa_embedding.csv'
    embed_df = pd.DataFrame(qoppa_embedded, columns=[f'Qoppa_t+{i*embedding_delay}' for i in range(embedding_dim)])
    embed_df.to_csv(embed_out_file, index=False)
    print(f"✅ Embedded Takens trajectory saved to: {embed_out_file}")

    return time, qoppa, delta_P, dSdt

# --- Run Section ---

def main():
    # Change the filename below to match your actual file
    filename = "256BB0_pax1000_2_measurements.csv"
    timestep = 0.01  # seconds between measurements (adjust as needed)

    time, qoppa, delta_P, dSdt = analyze_polarimeter_data_from_azimuth_ellipticity(filename, timestep)

if __name__ == "__main__":
    main()

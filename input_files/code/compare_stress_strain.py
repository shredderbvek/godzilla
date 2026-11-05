#!/usr/bin/env python3
"""
compare_stress_strain.py

Compares the uniaxial stress-strain curves of:
1. Irradiated F321 austenitic stainless steel (dpa = 2.85)
2. Unirradiated baseline F321 austenitic stainless steel (dpa = 0.0)

Constitutive model: Busso-Orowan Crystal Plasticity with irradiation loop defect hardening.
Reference: Liu, Nie, & Lin (2022), Frontiers in Materials, 9:823539.
"""

import os
import sys
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
try:
    import seaborn as sns
    sns.set_theme()
except ImportError:
    pass

def find_file(filename, search_dirs):
    """Find a file in a list of candidate directories."""
    for d in search_dirs:
        path = d / filename
        if path.is_file():
            return path
    return None

def main():
    script_dir = Path(__file__).resolve().parent
    repo_root = script_dir.parent.parent

    search_dirs = [
        script_dir.parent,      # input_files/
        script_dir,             # input_files/code/
        repo_root,              # godzilla/
        Path.cwd(),             # current working directory
    ]

    irr_csv_name = "polycrystal_baseline_out.csv"
    unirr_csv_name = "polycrystal_irradiated_out.csv"

    irr_path = find_file(irr_csv_name, search_dirs)
    unirr_path = find_file(unirr_csv_name, search_dirs)

    if not irr_path:
        print(f"Error: Could not locate '{irr_csv_name}' in search paths.")
        sys.exit(1)
    if not unirr_path:
        print(f"Error: Could not locate '{unirr_csv_name}' in search paths.")
        sys.exit(1)

    print(f"Loading irradiated data from:   {irr_path}")
    print(f"Loading unirradiated data from: {unirr_path}")

    # Columns: time, strain_zz, stress_zz
    irr_data = np.loadtxt(irr_path, delimiter=',', skiprows=1)
    unirr_data = np.loadtxt(unirr_path, delimiter=',', skiprows=1)

    t_irr, avg_disp_irr, stress_irr = irr_data[:, 0], irr_data[:, 1], irr_data[:, 2]
    t_unirr, avg_disp_unirr, stress_unirr = unirr_data[:, 0], unirr_data[:, 1], unirr_data[:, 2]

    # In the single-element test with pull_z = 0.002 * t on front face (z=1) and fix_z on back face (z=0),
    # the postprocessor 'strain_zz' evaluates ElementAverageValue(disp_z) = U_z / 2.
    # Therefore, the axial engineering strain is epsilon_zz = U_z / L = 2 * avg_disp_z = 0.002 * t.
    eng_strain_irr = 2.0 * avg_disp_irr * 100.0        # convert to % strain
    eng_strain_unirr = 2.0 * avg_disp_unirr * 100.0    # convert to % strain

    # Print summary metrics
    print("\n" + "=" * 70)
    print(" CRYSTAL PLASTICITY VERIFICATION COMPARISON")
    print(" Busso-Orowan Model with Irradiation Hardening (Liu et al. 2022)")
    print("=" * 70)
    print(f"{'Applied Strain (%)':<20} | {'Irradiated (2.85 dpa)':<22} | {'Unirradiated (0 dpa)':<20} | {'Hardening Delta (MPa)':<20}")
    print("-" * 70)

    # Compare at key strain levels
    common_strains = [0.0, 0.1, 0.2, 0.5, 1.0, 1.5, 2.0, 2.5, 3, 3.5, 4.0, 4.5, 5 ]
    for target_strain in common_strains:
        idx_irr = np.argmin(np.abs(eng_strain_irr - target_strain))
        idx_unirr = np.argmin(np.abs(eng_strain_unirr - target_strain))
        s_irr = stress_irr[idx_irr]
        s_unirr = stress_unirr[idx_unirr]
        delta = s_irr - s_unirr
        print(f"{eng_strain_irr[idx_irr]:>16.3f} % | {s_irr:>18.2f} MPa | {s_unirr:>16.2f} MPa | {delta:>16.2f} MPa")
    print("=" * 70 + "\n")

    # Plot comparison curves
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

    # --- Full Stress-Strain Curve ---
    ax1.plot(eng_strain_irr, stress_irr, 'o-', color='#D62728', linewidth=2.2, markersize=5,
             label='Irradiated (2.85 dpa, $N_i = 5.23\\times 10^{13}\\;\\mathrm{mm}^{-3}$)')
    ax1.plot(eng_strain_unirr, stress_unirr, 's--', color='#1F77B4', linewidth=2.0, markersize=5,
             label='Unirradiated Baseline (0.0 dpa, $N_i = 0$)')

    ax1.set_xlabel('Axial Engineering Strain $\\varepsilon_{zz}$ (%)', fontsize=12, fontweight='bold')
    ax1.set_ylabel('Axial Stress $\\sigma_{zz}$ (MPa)', fontsize=12, fontweight='bold')
    ax1.set_title('Uniaxial Tensile Response Comparison', fontsize=13, fontweight='bold')
    ax1.grid(True, linestyle=':', alpha=0.6)
    ax1.legend(loc='lower right', frameon=True, fontsize=10)

    # Annotate irradiation hardening gap
    mid_idx = np.argmin(np.abs(eng_strain_irr - 1.0))
    delta_mid = stress_irr[mid_idx] - stress_unirr[mid_idx]
    ax1.annotate(
        f'$\\Delta\\sigma \\approx +{delta_mid:.1f}$ MPa\n(Irradiation Hardening)',
        xy=(eng_strain_irr[mid_idx], (stress_irr[mid_idx] + stress_unirr[mid_idx]) / 2),
        xytext=(eng_strain_irr[mid_idx] - 0.4, (stress_irr[mid_idx] + stress_unirr[mid_idx]) / 2 + 300),
        arrowprops=dict(facecolor='black', arrowstyle='->', lw=1.2),
        bbox=dict(boxstyle='round,pad=0.4', facecolor='#FFF8DC', edgecolor='#D2B48C', alpha=0.9),
        fontsize=10
    )

    # --- Elastic-to-Yield Transition Zoom ---
    zoom_mask_irr = eng_strain_irr <= 0.4
    zoom_mask_unirr = eng_strain_unirr <= 0.4

    ax2.plot(eng_strain_irr[zoom_mask_irr], stress_irr[zoom_mask_irr], 'o-', color='#D62728',
             linewidth=2.2, markersize=6, label='Irradiated (2.85 dpa)')
    ax2.plot(eng_strain_unirr[zoom_mask_unirr], stress_unirr[zoom_mask_unirr], 's--', color='#1F77B4',
             linewidth=2.0, markersize=6, label='Unirradiated Baseline (0.0 dpa)')

    ax2.set_xlabel('Axial Engineering Strain $\\varepsilon_{zz}$ (%)', fontsize=12, fontweight='bold')
    ax2.set_ylabel('Axial Stress $\\sigma_{zz}$ (MPa)', fontsize=12, fontweight='bold')
    ax2.set_title('Elastic Loading & Initial Yielding (<= 0.4% strain)', fontsize=13, fontweight='bold')
    ax2.grid(True, linestyle=':', alpha=0.6)
    ax2.legend(loc='lower right', frameon=True, fontsize=10)

    # Calculate initial slope (Young's modulus)
    e_mod = (stress_irr[1] - stress_irr[0]) / (eng_strain_irr[1] / 100.0) / 1000.0  # in GPa
    ax2.text(0.05, 0.85, f'Initial $E \\approx {e_mod:.1f}$ GPa\n(Elastic slope match)',
             transform=ax2.transAxes,
             bbox=dict(boxstyle='round,pad=0.4', facecolor='white', edgecolor='gray', alpha=0.9),
             fontsize=10)

    plt.tight_layout()

    out_fig_dir = script_dir.parent  # save in input_files/
    out_fig_path = out_fig_dir / "stress_strain_comparison_20grn.png"
    plt.savefig(out_fig_path, dpi=300)
    print(f"Saved comparison plot to: {out_fig_path}")

    # Also save in script_dir if different
    if script_dir != out_fig_dir:
        plt.savefig(script_dir / "stress_strain_comparison_20grn.png", dpi=300)

    plt.close()

if __name__ == "__main__":
    main()

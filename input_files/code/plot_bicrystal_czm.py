#!/usr/bin/env python3
"""
plot_bicrystal_czm.py

Compares the mechanical response and grain boundary damage evolution of:
1. Irradiated bicrystal (dpa = 2.85, Busso-Orowan CP + Bilinear CZM)
2. Unirradiated baseline bicrystal (dpa = 0.0, Busso-Orowan CP + Bilinear CZM)

Generates publication-quality comparison plots with non-overlapping legends and clear annotations:
- Panel 1: Tensile stress-strain response (stress_zz vs. strain_zz)
- Panel 2: Grain boundary cohesive damage evolution (D vs. strain_zz)
- Panel 3: Grain matrix plastic strain accumulation ((F^p_zz - 1) * 100%)
"""

import sys
import shutil
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt

try:
    import seaborn as sns
    sns.set_theme(style='whitegrid')
except ImportError:
    pass

def find_file(filename, search_dirs):
    for d in search_dirs:
        p = d / filename
        if p.is_file():
            return p
    return None

def main():
    script_dir = Path(__file__).resolve().parent
    repo_root = script_dir.parent.parent

    search_dirs = [
        repo_root,
        script_dir.parent,
        script_dir,
        Path.cwd(),
    ]

    irr_csv = find_file("bicrystal_irradiated_czm_out.csv", search_dirs)
    unirr_csv = find_file("bicrystal_unirradiated_czm_out.csv", search_dirs)

    if not irr_csv or not unirr_csv:
        print(f"Error: Could not locate bicrystal CZM CSV files in {search_dirs}")
        sys.exit(1)

    print(f"Loading irradiated bicrystal data from:   {irr_csv}")
    print(f"Loading unirradiated bicrystal data from: {unirr_csv}")

    # Columns: time (0), disp_z_top (1), fp_zz_grain1 (2), fp_zz_grain2 (3), gb_damage (4), strain_zz (5), stress_zz (6)
    irr_data = np.loadtxt(irr_csv, delimiter=',', skiprows=1)
    unirr_data = np.loadtxt(unirr_csv, delimiter=',', skiprows=1)

    t_irr, dmg_irr, eps_irr, s_irr = irr_data[:, 0], irr_data[:, 4], irr_data[:, 5] * 100.0, irr_data[:, 6]
    fp1_irr, fp2_irr = np.maximum(irr_data[:, 2] - 1.0, 0.0) * 100.0, np.maximum(irr_data[:, 3] - 1.0, 0.0) * 100.0

    t_unirr, dmg_unirr, eps_unirr, s_unirr = unirr_data[:, 0], unirr_data[:, 4], unirr_data[:, 5] * 100.0, unirr_data[:, 6]
    fp1_unirr, fp2_unirr = np.maximum(unirr_data[:, 2] - 1.0, 0.0) * 100.0, np.maximum(unirr_data[:, 3] - 1.0, 0.0) * 100.0

    # Summary table output to terminal
    print("\n" + "=" * 80)
    print(" BICRYSTAL GRAIN BOUNDARY CZM & IRRADIATION COMPARISON ")
    print("=" * 80)
    print(f"{'Metric':<35} | {'Irradiated (2.85 dpa)':<20} | {'Unirradiated (0.0 dpa)':<20}")
    print("-" * 80)
    print(f"{'Peak Normal Stress (MPa)':<35} | {np.max(s_irr):>18.2f} | {np.max(s_unirr):>18.2f}")

    idx_dmg_init_irr = np.where(dmg_irr > 0.01)[0]
    idx_dmg_init_unirr = np.where(dmg_unirr > 0.01)[0]
    init_strain_irr = eps_irr[idx_dmg_init_irr[0]] if len(idx_dmg_init_irr) > 0 else 0.0
    init_strain_unirr = eps_unirr[idx_dmg_init_unirr[0]] if len(idx_dmg_init_unirr) > 0 else 0.0
    print(f"{'GB Damage Initiation Strain (%)':<35} | {init_strain_irr:>18.3f} % | {init_strain_unirr:>18.3f} %")

    print(f"{'Peak Grain 1 Plastic Strain (%)':<35} | {np.max(fp1_irr):>18.4f} % | {np.max(fp1_unirr):>18.4f} %")
    print(f"{'Peak Grain 2 Plastic Strain (%)':<35} | {np.max(fp2_irr):>18.4f} % | {np.max(fp2_unirr):>18.4f} %")
    print("=" * 80 + "\n")

    # Create 3-panel figure with generous vertical proportions
    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(10, 13), sharex=True)

    # ------------------ Panel 1: Stress-Strain Response ------------------
    ax1.plot(eps_irr, s_irr, 'r-o', linewidth=2.2, markersize=4,
             label=r'Irradiated (2.85 dpa, Hardened Matrix + CZM)')
    ax1.plot(eps_unirr, s_unirr, 'b--s', linewidth=2.0, markersize=4,
             label=r'Unirradiated Baseline (0.0 dpa, Ductile Matrix + CZM)')

    ax1.axhline(900.0, color='darkgray', linestyle=':', linewidth=1.8,
                label=r'CZM Cohesive Strength $\sigma_c = 900$ MPa')
    ax1.set_ylabel(r'Tensile Stress $\sigma_{zz}$ (MPa)', fontsize=12, fontweight='bold')
    ax1.set_title('Bicrystal Tensile Response & Intergranular Failure\nCrystal Plasticity (Busso-Orowan) with Cohesive Zone Model (CZM)',
                  fontsize=13, fontweight='bold')
    ax1.set_ylim(-30, 1180)

    # Place legend in upper right quadrant where stress has softened to zero (completely clear of curves)
    ax1.legend(loc='upper right', frameon=True, framealpha=0.92, fontsize=10)
    ax1.grid(True, linestyle='--', alpha=0.6)

    # Clean annotations positioned in clear zones above the curves
    max_idx_irr = np.argmax(s_irr)
    ax1.annotate(f'Irradiated Peak:\n{s_irr[max_idx_irr]:.1f} MPa ({eps_irr[max_idx_irr]:.3f}%)',
                 xy=(eps_irr[max_idx_irr], s_irr[max_idx_irr]),
                 xytext=(eps_irr[max_idx_irr] - 0.28, 980),
                 arrowprops=dict(facecolor='darkred', edgecolor='darkred', shrink=0.08, width=1.0, headwidth=5),
                 fontsize=9, fontweight='bold',
                 bbox=dict(boxstyle='round,pad=0.3', facecolor='#FFE4E1', edgecolor='darkred', alpha=0.9))

    max_idx_unirr = np.argmax(s_unirr)
    ax1.annotate(f'Unirradiated Peak:\n{s_unirr[max_idx_unirr]:.1f} MPa ({eps_unirr[max_idx_unirr]:.3f}%)\n(Plastic Delay)',
                 xy=(eps_unirr[max_idx_unirr], s_unirr[max_idx_unirr]),
                 xytext=(eps_unirr[max_idx_unirr] + 0.08, 970),
                 arrowprops=dict(facecolor='darkblue', edgecolor='darkblue', shrink=0.08, width=1.0, headwidth=5),
                 fontsize=9, fontweight='bold',
                 bbox=dict(boxstyle='round,pad=0.3', facecolor='#E6F2FF', edgecolor='darkblue', alpha=0.9))

    # ------------------ Panel 2: Grain Boundary Cohesive Damage ------------------
    ax2.plot(eps_irr, dmg_irr, 'r-o', linewidth=2.2, markersize=4,
             label=r'Irradiated GB Damage $D$ (Early Initiation at $\varepsilon=0.507\%$)')
    ax2.plot(eps_unirr, dmg_unirr, 'b--s', linewidth=2.0, markersize=4,
             label=r'Unirradiated GB Damage $D$ (Delayed Initiation at $\varepsilon=0.576\%$)')

    ax2.axhline(1.0, color='darkred', linestyle=':', linewidth=1.5, label=r'Full Separation ($D = 1.0$)')
    ax2.set_ylabel('Grain Boundary Damage $D$', fontsize=12, fontweight='bold')
    ax2.set_ylim(-0.05, 1.25)

    # Place legend in upper left where D=0 for strain < 0.5% (completely clear)
    ax2.legend(loc='upper left', frameon=True, framealpha=0.92, fontsize=10)
    ax2.grid(True, linestyle='--', alpha=0.6)

    # Indicate damage initiation using clean vertical dotted indicator lines and lower annotations
    if init_strain_irr > 0 and init_strain_unirr > 0:
        ax2.axvline(init_strain_irr, color='red', linestyle='--', linewidth=1.2, alpha=0.7)
        ax2.axvline(init_strain_unirr, color='blue', linestyle='--', linewidth=1.2, alpha=0.7)

        ax2.annotate(f'Early Onset:\n$\\varepsilon = {init_strain_irr:.3f}\\%$',
                     xy=(init_strain_irr, 0.05),
                     xytext=(init_strain_irr - 0.18, 0.18),
                     arrowprops=dict(facecolor='red', edgecolor='red', shrink=0.05, width=1.0, headwidth=5),
                     fontsize=9, fontweight='bold',
                     bbox=dict(boxstyle='round,pad=0.3', facecolor='#FFE4E1', edgecolor='red', alpha=0.9))

        ax2.annotate(f'Delayed Onset (+13.6%):\n$\\varepsilon = {init_strain_unirr:.3f}\\%$',
                     xy=(init_strain_unirr, 0.05),
                     xytext=(init_strain_unirr + 0.04, 0.18),
                     arrowprops=dict(facecolor='blue', edgecolor='blue', shrink=0.05, width=1.0, headwidth=5),
                     fontsize=9, fontweight='bold',
                     bbox=dict(boxstyle='round,pad=0.3', facecolor='#E6F2FF', edgecolor='blue', alpha=0.9))

    # ------------------ Panel 3: Grain Matrix Plastic Strain ------------------
    ax3.plot(eps_unirr, fp1_unirr, 'b-', linewidth=2.2, label=r'Unirradiated Grain 1 Plastic Strain $(F^p_{zz}-1)$')
    ax3.plot(eps_unirr, fp2_unirr, 'c--', linewidth=2.0, label=r'Unirradiated Grain 2 Plastic Strain $(F^p_{zz}-1)$')
    ax3.plot(eps_irr, fp1_irr, 'r-', linewidth=2.2, label=r'Irradiated Grain 1 Plastic Strain ($\approx 0\%$, Elastic Embrittlement)')
    ax3.plot(eps_irr, fp2_irr, 'm--', linewidth=2.0, label=r'Irradiated Grain 2 Plastic Strain ($\approx 0\%$)')

    ax3.set_xlabel(r'Total Engineering Strain $\varepsilon_{zz}$ (%)', fontsize=12, fontweight='bold')
    ax3.set_ylabel(r'Plastic Strain $(F^p_{zz}-1)$ (%)', fontsize=12, fontweight='bold')
    ax3.set_ylim(-0.008, 0.130)

    # Place 2-column legend in the top headroom region (y > 0.095) above the curve plateau
    ax3.legend(loc='upper left', ncol=2, frameon=True, framealpha=0.92, fontsize=9.5)
    ax3.grid(True, linestyle='--', alpha=0.6)

    # Annotate plateau with clean arrow
    ax3.annotate('Plastic flow blunts interface\nstress buildup (Ductile Shielding)',
                 xy=(0.75, np.max(fp2_unirr)),
                 xytext=(0.58, 0.045),
                 arrowprops=dict(facecolor='navy', edgecolor='navy', shrink=0.06, width=1.0, headwidth=5),
                 fontsize=9, fontweight='bold',
                 bbox=dict(boxstyle='round,pad=0.3', facecolor='#F0F8FF', edgecolor='navy', alpha=0.9))

    plt.tight_layout()

    out_file = script_dir / 'bicrystal_czm_damage_stress_strain.png'
    plt.savefig(out_file, dpi=300)
    print(f"Saved figure to: {out_file}")

    # Copy to doc directory
    doc_dir = repo_root / 'doc'
    if doc_dir.exists():
        doc_file = doc_dir / 'bicrystal_czm_damage_stress_strain.png'
        shutil.copy(out_file, doc_file)
        print(f"Copied figure to: {doc_file}")

    # Copy to brain artifact directory
    brain_dir = Path("/home/ghostrobot96/.gemini/antigravity-cli/brain/b43c565b-d747-4a07-ae35-41353d8717ac")
    if brain_dir.exists():
        brain_file = brain_dir / 'bicrystal_czm_damage_stress_strain.png'
        shutil.copy(out_file, brain_file)
        print(f"Copied figure to brain artifact directory: {brain_file}")

    plt.close()

if __name__ == '__main__':
    main()

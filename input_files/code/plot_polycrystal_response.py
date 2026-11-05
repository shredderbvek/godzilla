import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import shutil

# Apply user's preferred seaborn theme
sns.set_theme(style='whitegrid')

# Resolve paths
code_dir = Path(__file__).resolve().parent
project_dir = code_dir.parent.parent

csv_path = project_dir / 'polycrystal_irradiated_out.csv'
if not csv_path.exists():
    csv_path = code_dir.parent / 'polycrystal_irradiated_out.csv'

data = np.loadtxt(csv_path, delimiter=',', skiprows=1)

# Columns: time (0), e_zz (1), fp_zz (2), gss (3), pk2 (4), slip_increment (5), stress_zz (6)
time = data[:, 0]
strain_zz = data[:, 1]
fp_zz = data[:, 2]
gss = data[:, 3]
pk2 = data[:, 4]
slip_inc = np.abs(data[:, 5])
stress_zz = data[:, 6]

# Convert strain to percentage
strain_pct = strain_zz * 100.0
plastic_strain_pct = (fp_zz - 1.0) * 100.0

fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(9, 8), sharex=True)

# ----------------- Panel 1: Stress-Strain Response -----------------
ax1.plot(strain_pct, stress_zz, 'r-', linewidth=2.2, label=r'Cauchy Stress $\sigma_{zz}$ (2.85 dpa)')
ax1.plot(strain_pct, pk2, 'b--', linewidth=1.8, label=r'PK2 Stress $S_{zz}$')

# Annotate yield point (~814.56 MPa at strain ~0.415%)
yield_mask = fp_zz > 1.00000001
if np.any(yield_mask):
    idx_yield = np.where(yield_mask)[0][0]
    ax1.plot(strain_pct[idx_yield], stress_zz[idx_yield], 'ko', markersize=7, label=f'Yield Onset (~{stress_zz[idx_yield]:.1f} MPa)')
    ax1.annotate(f'Yield: {stress_zz[idx_yield]:.1f} MPa\n$\\varepsilon_{{zz}}={strain_pct[idx_yield]:.3f}\\%$',
                 xy=(strain_pct[idx_yield], stress_zz[idx_yield]),
                 xytext=(strain_pct[idx_yield] - 0.15, stress_zz[idx_yield] + 60),
                 arrowprops=dict(facecolor='black', shrink=0.05, width=1.2, headwidth=6),
                 fontsize=10, fontweight='bold', bbox=dict(boxstyle='round,pad=0.3', facecolor='yellow', alpha=0.6))

ax1.set_ylabel('Stress (MPa)', fontsize=12, fontweight='bold')
ax1.set_title('20-Grain Irradiated Polycrystal (316L, 2.85 dpa, 573 K)\nElastic-Plastic Tensile & Hardening Response', fontsize=13, fontweight='bold')
ax1.legend(loc='lower right', frameon=True, framealpha=0.9, fontsize=10)
ax1.grid(True, linestyle='--', alpha=0.7)

# ----------------- Panel 2: Plastic Flow & Hardening -----------------
color_fp = 'tab:green'
ax2.plot(strain_pct, plastic_strain_pct, color=color_fp, linewidth=2.0, label=r'Plastic Strain $(F^p_{zz}-1.0)\times 100\%$')
ax2.set_ylabel(r'Plastic Strain $(F^p_{zz}-1.0)$ (%)', color=color_fp, fontsize=12, fontweight='bold')
ax2.tick_params(axis='y', labelcolor=color_fp)
ax2.set_xlabel('Total Strain $\\varepsilon_{zz}$ (%)', fontsize=12, fontweight='bold')

ax2_twin = ax2.twinx()
color_gss = 'tab:purple'
ax2_twin.plot(strain_pct, gss, color=color_gss, linestyle='-.', linewidth=2.0, label=r'Slip Resistance $g_{ss}$ (MPa)')
ax2_twin.set_ylabel(r'Slip Resistance $g_{ss}$ (MPa)', color=color_gss, fontsize=12, fontweight='bold')
ax2_twin.tick_params(axis='y', labelcolor=color_gss)

# Combine legends for panel 2
lines_1, labels_1 = ax2.get_legend_handles_labels()
lines_2, labels_2 = ax2_twin.get_legend_handles_labels()
ax2.legend(lines_1 + lines_2, labels_1 + labels_2, loc='upper left', frameon=True, framealpha=0.9, fontsize=10)
ax2.grid(True, linestyle='--', alpha=0.7)

plt.tight_layout()

# Save output plots
output_fig = code_dir / 'polycrystal_stress_strain.png'
plt.savefig(output_fig, dpi=300)
print(f"Saved plot to: {output_fig}")

# Copy to doc directory
doc_fig = project_dir / 'doc' / 'polycrystal_stress_strain.png'
shutil.copy(output_fig, doc_fig)
print(f"Copied plot to: {doc_fig}")

# Copy to brain artifact directory
brain_dir = Path('/home/ghostrobot96/.gemini/antigravity-cli/brain/b43c565b-d747-4a07-ae35-41353d8717ac')
if brain_dir.exists():
    shutil.copy(output_fig, brain_dir / 'polycrystal_stress_strain.png')
    print(f"Copied plot to brain artifact directory: {brain_dir / 'polycrystal_stress_strain.png'}")

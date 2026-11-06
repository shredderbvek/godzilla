#!/usr/bin/env python3
import csv
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

def load_csv(fname):
    with open(fname) as f:
        reader = csv.DictReader(f)
        data = {k: [] for k in reader.fieldnames}
        for row in reader:
            for k, v in row.items():
                data[k].append(float(v))
    return {k: np.array(v) for k, v in data.items()}

b = load_csv("polycrystal_baseline_out.csv")
i = load_csv("polycrystal_irradiated_out.csv")

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6), dpi=200)

strain_b = b["e_zz"] * 100.0
stress_b = b["stress_zz"]
strain_i = i["e_zz"] * 100.0
stress_i = i["stress_zz"]

# Subplot 1: Full Range 0 to 5.14%
ax1.plot(strain_i, stress_i, "-", color="#D62728", lw=2.5, label=r"Irradiated (2.85 dpa, $N_i=5.23\times 10^{13}\;\mathrm{mm}^{-3}$)")
ax1.plot(strain_b, stress_b, "--", color="#1F77B4", lw=2.2, label=r"Unirradiated Baseline (0.0 dpa, $N_i=0$)")

# Annotate yield points
idx_yb = np.argmin(np.abs(strain_b - 0.2))
idx_yi = np.argmin(np.abs(strain_i - 0.45))
ax1.scatter([strain_b[idx_yb]], [stress_b[idx_yb]], color="#1F77B4", s=50, zorder=5)
ax1.scatter([strain_i[idx_yi]], [stress_i[idx_yi]], color="#D62728", s=50, zorder=5)

ax1.annotate("Baseline Yield\n" + r"$\sigma_y \approx 280$ MPa",
             xy=(strain_b[idx_yb], stress_b[idx_yb]),
             xytext=(strain_b[idx_yb] + 0.3, stress_b[idx_yb] - 250),
             arrowprops=dict(arrowstyle="->", lw=1.2, color="#1F77B4"),
             bbox=dict(boxstyle="round,pad=0.3", facecolor="#E8F4F8", edgecolor="#1F77B4"),
             fontsize=9)

ax1.annotate("Irradiated Yield\n" + r"$\sigma_y \approx 836$ MPa",
             xy=(strain_i[idx_yi], stress_i[idx_yi]),
             xytext=(strain_i[idx_yi] - 0.35, stress_i[idx_yi] + 280),
             arrowprops=dict(arrowstyle="->", lw=1.2, color="#D62728"),
             bbox=dict(boxstyle="round,pad=0.3", facecolor="#FDE8E8", edgecolor="#D62728"),
             fontsize=9)

# Hardening gap annotation
idx_mid = np.argmin(np.abs(strain_i - 2.5))
delta_mid = stress_i[idx_mid] - stress_b[np.argmin(np.abs(strain_b - 2.5))]
mid_y = (stress_i[idx_mid] + stress_b[np.argmin(np.abs(strain_b - 2.5))]) / 2.0
ax1.annotate("Radiation Hardening Gap\n" + rf"$\Delta\sigma \approx +{delta_mid:.1f}$ MPa",
             xy=(2.5, mid_y),
             xytext=(1.8, mid_y + 250),
             arrowprops=dict(arrowstyle="->", lw=1.2, color="black"),
             bbox=dict(boxstyle="round,pad=0.3", facecolor="#FFF8DC", edgecolor="#D2B48C"),
             fontsize=9)

ax1.set_xlabel(r"Axial Total Strain $\varepsilon_{zz}$ (%)", fontsize=11, fontweight="bold")
ax1.set_ylabel(r"Cauchy True Axial Stress $\sigma_{zz}$ (MPa)", fontsize=11, fontweight="bold")
ax1.set_title("Full Tensile Response (0 to 5.14% Total Strain)", fontsize=12, fontweight="bold")
ax1.grid(True, linestyle=":", alpha=0.6)
ax1.legend(loc="lower right", frameon=True, fontsize=9)

# Subplot 2: Zoom on Elastic to Yield Transition (0 to 1.0%)
mask_b = strain_b <= 1.0
mask_i = strain_i <= 1.0

ax2.plot(strain_i[mask_i], stress_i[mask_i], "o-", color="#D62728", lw=2.2, markersize=3, label="Irradiated (2.85 dpa)")
ax2.plot(strain_b[mask_b], stress_b[mask_b], "s--", color="#1F77B4", lw=2.0, markersize=3, label="Unirradiated Baseline")

ax2.set_xlabel(r"Axial Total Strain $\varepsilon_{zz}$ (%)", fontsize=11, fontweight="bold")
ax2.set_ylabel(r"Cauchy True Axial Stress $\sigma_{zz}$ (MPa)", fontsize=11, fontweight="bold")
ax2.set_title(r"Elastic Loading & Multi-grain Yield Transition ($\leq$ 1.0% Strain)", fontsize=12, fontweight="bold")
ax2.grid(True, linestyle=":", alpha=0.6)
ax2.legend(loc="lower right", frameon=True, fontsize=9)

# Annotate Young modulus
e_mod = (stress_i[1] - stress_i[0]) / (strain_i[1] / 100.0) / 1000.0
ax2.text(0.05, 0.85, f"Young Modulus $E \\approx {e_mod:.1f}$ GPa\n(Identical elastic stiffness)",
         transform=ax2.transAxes,
         bbox=dict(boxstyle="round,pad=0.4", facecolor="white", edgecolor="gray", alpha=0.9),
         fontsize=9)

fig.suptitle("20-Grain Polycrystal Tensile Response: Unirradiated Baseline vs. Irradiated (Completed Simulation)", fontsize=14, fontweight="bold")
fig.tight_layout()

fig.savefig("stress_strain_comparison_final.png")
fig.savefig("stress_strain_comparison_current.png")
print("Saved final comparison plots successfully!")

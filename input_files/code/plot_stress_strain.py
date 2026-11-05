import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

# Apply user's preferred seaborn theme
sns.set_theme()

# Resolve path to input CSV files
base_dir = Path(__file__).resolve().parent
input_dir = base_dir.parent if (base_dir.parent / 'test_single_element_out.csv').exists() else base_dir

file_irradiated = input_dir / 'test_single_element_out.csv'
file_unirradiated = input_dir / 'test_single_element_unirradiated_baseline_out.csv'

# Load numerical CSV, skipping 1-row header
# Columns: time (0), strain_zz (1), stress_zz (2)
data_irr = np.loadtxt(file_irradiated, delimiter=',', skiprows=1)
data_unirr = np.loadtxt(file_unirradiated, delimiter=',', skiprows=1)

# strain_zz in CSV is element-averaged disp_z (U_z / 2); engineering strain is 2 * strain_zz
strain_irr = 2.0 * data_irr[:, 1]
stress_irr = data_irr[:, 2]

strain_unirr = 2.0 * data_unirr[:, 1]
stress_unirr = data_unirr[:, 2]

# Plot comparison curves
plt.figure(figsize=(8, 5))
plt.plot(strain_irr, stress_irr, linestyle='-', color='r', label='Irradiated (2.85 dpa)')
plt.plot(strain_unirr, stress_unirr, linestyle='--', color='b', label='Unirradiated Baseline')

plt.xlabel('Engineering Strain')
plt.ylabel('Stress (MPa)')
plt.title('Stress-Strain Response Comparison')
plt.legend(loc='lower right')
plt.grid(True)

output_fig = input_dir / 'Stress-Strain Response Comparison.png'
plt.savefig(output_fig, dpi=300)
print(f"Saved plot to: {output_fig}")
plt.show()

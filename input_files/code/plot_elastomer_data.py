import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
sns.set_theme()
# Load numerical CSV, skipping a 1-row header if it exists
#data = np.loadtxt('pu_dcb_synthetic.csv', delimiter=',', skiprows=1)
#dcb_pu_moose_bilinear_no_fbar_pin25_refine_0p05_lin_elastic_one_orientation_qp_all.csv
data = np.loadtxt('pu_dcb_prod_case_1.csv', delimiter=',', skiprows=1)

u = data[:, 6]
P_CZM = data[:, 1]  # Full 2.5 mm specimen force, not the 1 mm reaction.

data_literature = np.loadtxt('p_vs_u_digitized_fine.csv', delimiter=',', skiprows=1)

u_literature = data_literature[:, 0]
P_sharp = data_literature[:, 1]
P_phase_field = data_literature[:, 2]
P_AT1 = data_literature[:, 3]

plt.figure(figsize=(8, 5))
plt.plot(u, P_CZM, linestyle='-', color='g', label='CZM')
# plt.plot(u_literature, P_sharp, linestyle='--', color='r', label='Sharp')
# plt.plot(u_literature, P_phase_field, linestyle='-', color='b', label='Phase field')
plt.xlabel('u (mm)')
plt.ylabel('P (N)')
plt.title('Force-Displacement Response')
plt.legend(loc='lower right')
plt.grid(True)
plt.savefig('Force-Displacement Response CZM.png', dpi=300)
plt.show()

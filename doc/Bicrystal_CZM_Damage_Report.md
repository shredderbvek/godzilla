# Bicrystal Crystal Plasticity & Cohesive Zone Modeling (CZM) Report

## 1. Executive Summary

A 3D bicrystal simulation has been developed to investigate the coupled effect of **matrix irradiation hardening** and **intergranular cohesive fracture** in austenitic stainless steel (316L). The simulation couples:
1. **Bulk Grains:** The rate-dependent Busso-Orowan crystal plasticity constitutive model ([`CrystalPlasticityBussoOrowanIrradiationUpdate`](file:///home/ghostrobot96/projects/godzilla/include/materials/CrystalPlasticityBussoOrowanIrradiationUpdate.h)), modeling dislocation glide, proliferation, and dispersed barrier hardening from Frank interstitial loops.
2. **Grain Boundary Interface:** A mixed-mode bilinear cohesive zone model ([`BiLinearMixedModeTraction`](file:///home/ghostrobot96/projects/moose/modules/solid_mechanics/include/materials/cohesive_zone_model/BiLinearMixedModeTraction.h)) implemented on the internal grain boundary interface separating the two crystals.

Two comparative cases were simulated under monotonic uniaxial tension along the grain boundary normal ($z$-axis):
* **Irradiated Specimen ($2.85\text{ dpa}$):** Hardened grain matrix ($N_i = 5.23\times 10^{13}\;\text{mm}^{-3}$, $g_{ss} = 336.27\text{ MPa}$).
* **Baseline Specimen ($0.0\text{ dpa}$):** Unirradiated ductile grain matrix ($N_i = 0$, $g_{ss} = 33.86\text{ MPa}$).

---

## 2. Model Architecture & Boundary Value Problem

### A. Bicrystal Geometry & Discretization
* **Domain:** $1.0\times 1.0\times 2.0\;\text{mm}^3$ rectangular bicrystal column.
  - **Grain 1 (Block 1):** $z \in [0.0, 1.0]\;\text{mm}$, Bunge Euler angles $(\phi_1=25.0^\circ, \Phi=40.0^\circ, \phi_2=15.0^\circ)$.
  - **Grain 2 (Block 2):** $z \in [1.0, 2.0]\;\text{mm}$, Bunge Euler angles $(\phi_1=85.0^\circ, \Phi=30.0^\circ, \phi_2=60.0^\circ)$.
* **Internal Grain Boundary:** Split along $z = 1.0\;\text{mm}$ using MOOSE's `BreakMeshByBlockGenerator`, creating internal sideset `Block1_Block2`.
* **CZM Interface Formulation:** `Physics/SolidMechanics/CohesiveZone` action with `strain = FINITE`, enforcing traction continuity and displacement jump tracking via finite-strain total Lagrangian interface kernels.

### B. Cohesive Zone Model (CZM) Law
The grain boundary interface obeys a bilinear traction-separation law with damage evolution:
$$\mathbf{t} = (1 - D)\,\mathbf{K}\,\boldsymbol{\delta}$$
* **Penalty Elastic Stiffness:** $K = 1.0\times 10^6\;\text{MPa/mm}$ ($1000\;\text{GPa/mm}$)
* **Normal Cohesive Strength:** $\sigma_c = N = 900.0\;\text{MPa}$
* **Shear Cohesive Strength:** $\tau_c = S = 600.0\;\text{MPa}$
* **Critical Fracture Energy (Mode I):** $G_I^c = 8.0\;\text{N/mm}$ ($8.0\;\text{kJ/m}^2$)
* **Damage Evolution:** $D \in [0, 1]$, initiating when traction reaches $\sigma_c$, evolving linearly to $D = 1.0$ (complete separation) at critical jump $\delta_f = 2 G_I^c / \sigma_c = 17.78\;\mu\text{m}$.

### C. Boundary & Loading Conditions
* Back face ($z = 0$): $u_z = 0$
* Symmetry rollers: $u_x = 0$ on $x = 0$, $u_y = 0$ on $y = 0$
* Front face ($z = 2.0$): Uniaxial tensile extension $u_z(t) = 0.002 \cdot t$ (engineering strain rate $\dot{\varepsilon}_{zz} = 0.1\%/\text{s}$).

---

## 3. Comparative Results

```
================================================================================
           BICRYSTAL GRAIN BOUNDARY CZM & IRRADIATION COMPARISON
================================================================================
Metric                              | Irradiated (2.85 dpa) | Unirradiated (0.0 dpa)
--------------------------------------------------------------------------------
Peak Normal Stress                  |             890.49 MPa|             893.09 MPa
GB Damage Initiation Strain         |              0.507 %  |              0.576 %
Strain at Complete Separation (D=1) |              0.957 %  |              0.983 %
Peak Grain 1 Plastic Strain (Fp-1)  |             0.0000 %  |             0.0815 %
Peak Grain 2 Plastic Strain (Fp-1)  |             0.0000 %  |             0.0887 %
================================================================================
```

![Bicrystal Stress-Strain and Damage Comparison](file:///home/ghostrobot96/projects/godzilla/doc/bicrystal_czm_damage_stress_strain.png)

---

## 4. Key Physical Findings

### 1. Matrix Plastic Shielding vs. Elastic Stress Concentration
* **Unirradiated Material ($0.0\text{ dpa}$):**
  - Dislocation glide initiates readily at low resolved shear stresses ($g_{ss} = 33.86\text{ MPa}$).
  - Grains 1 and 2 undergo visible macroscopic plastic slip ($F^p_{zz} - 1 = 0.0815\%$ and $0.0887\%$).
  - This bulk plastic flow relaxes the interfacial stress buildup, blunting the traction transferred to the grain boundary.
  - As a direct consequence, **grain boundary damage initiation is significantly delayed by $+13.6\%$ strain** ($\varepsilon_{zz} = 0.576\%$ vs. $0.507\%$).
* **Irradiated Material ($2.85\text{ dpa}$):**
  - Dense radiation loops pin dislocations, elevating the initial slip resistance tenfold to $g_{ss} = 336.27\text{ MPa}$.
  - The grain matrix cannot activate plastic slip prior to reaching the interface strength ($F^p_{zz} - 1 \approx 0.0000\%$).
  - All deformation remains elastic, transferring 100% of the elastic strain energy directly to the grain boundary.
  - The grain boundary hits the cohesive strength prematurely at $\varepsilon_{zz} = 0.507\%$, triggering immediate damage growth and intergranular failure.

### 2. Post-Peak Softening & Decohesion
* Once $D > 0$, both specimens enter the softening branch of the traction-separation law.
* Stress unloads from $\sim 890\text{ MPa}$ monotonically down to zero as $D \to 1.0$.
* The unirradiated specimen retains superior total energy dissipation due to the plastic work consumed in the bulk crystals prior to grain boundary rupture.

---

## 5. File Inventory

| File Path | Description |
| :--- | :--- |
| [`bicrystal_irradiated_czm.i`](file:///home/ghostrobot96/projects/godzilla/bicrystal_irradiated_czm.i) | Input file: Irradiated bicrystal ($2.85\text{ dpa}$) with CZM |
| [`bicrystal_unirradiated_czm.i`](file:///home/ghostrobot96/projects/godzilla/bicrystal_unirradiated_czm.i) | Input file: Unirradiated baseline bicrystal ($0.0\text{ dpa}$) with CZM |
| [`bicrystal_irradiated_czm_out.csv`](file:///home/ghostrobot96/projects/godzilla/bicrystal_irradiated_czm_out.csv) | CSV results for irradiated bicrystal |
| [`bicrystal_unirradiated_czm_out.csv`](file:///home/ghostrobot96/projects/godzilla/bicrystal_unirradiated_czm_out.csv) | CSV results for unirradiated baseline bicrystal |
| [`input_files/code/plot_bicrystal_czm.py`](file:///home/ghostrobot96/projects/godzilla/input_files/code/plot_bicrystal_czm.py) | Python plotting script for 3-panel comparison |
| [`doc/bicrystal_czm_damage_stress_strain.png`](file:///home/ghostrobot96/projects/godzilla/doc/bicrystal_czm_damage_stress_strain.png) | High-resolution publication comparison figure |

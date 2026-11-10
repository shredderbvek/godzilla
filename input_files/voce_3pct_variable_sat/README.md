# 3% nonlinear Voce — variable-saturation verification

Based on the previously successful `voce_sat_rate_m0050.i` input.

Both cases use the same 1-element FCC crystal geometry, Bunge Euler angles, elastic constants, and `CrystalPlasticityKalidindiVoceUpdate` model.

| Parameter | Value |
|---|---|
| `r` | 1.4 |
| `n_gss` | 2 |
| `h` | 190 MPa |
| `gss_initial` | 35 MPa |
| `gss_sat_initial` | 110 MPa |
| `ao_sat` | 1e-5 s^-1 |
| `xm_gss` | 0.005 |
| `is_gss_sat_constant` | false |
| `pull_z` | `0.003*t` -> 3% strain at 10 s |
| `dtmax` | 0.05 / 0.025 s |

## Run

Extract or copy the package and enter its directory:

```bash
/home/ghostrobot96/projects/godzilla/godzilla-opt -i voce_3pct_variable_sat_dt005.i
/home/ghostrobot96/projects/godzilla/godzilla-opt -i voce_3pct_variable_sat_dt0025.i
python3 check_voce_3pct.py
```

These simulations have **not been executed** in this environment; the input files were generated from the earlier working MOOSE test and checked for internal consistency.

The CSV outputs should have the names `voce_3pct_variable_sat_dt005_out.csv` and `voce_3pct_variable_sat_dt0025_out.csv`.

## Diagnostics

The input outputs:
- `gss_01_num` through `gss_12_num`: all 12 numerical slip-system resistances
- `Gamma_dot`: sum of absolute slip rates
- `Lambda_plane_1_dot` through `Lambda_plane_4_dot`: interaction-weighted slip-rate histories
- `strain_zz`: engineering strain from displacement of the loaded `z=1` face divided by `L0=1`
- `stress_zz`: mean axial stress
- `gs_formula_saved`: reconstructed saturation strength from **saved endpoint** slip rates
- `gs_minus_g0_saved`: admissibility indicator; should remain positive at saved steps

At the recorded slip rate, the reconstructed saturation is

`g_s = 110*(Gamma_dot/1e-5)^0.005` for `Gamma_dot > 0`, otherwise `g_s = 110`.

The checker integrates the independent scalar ODE for each plane:

`dg_p/dt = 190*((g_s(t)-g_p)/(g_s(t)-35))**2 * Lambda_dot_p(t)`

using piecewise-linear interpolation of **recorded** rates and RK4. It also evaluates a global-step backward-Euler residual. This is a **postprocessed-history verification**, not an exact reference for internal constitutive substeps, and rates are coupled to stresses in MOOSE. It should not be mistaken for experimental material validation.

## Directly outputting the saturation strength inside your C++ implementation

Currently `_gss_sat` is a **local C++ variable**, not a MOOSE material property. An `.i` input alone cannot access it directly. The provided `gs_formula_saved` checks the formula using exported converged endpoint rates instead; it **cannot reveal its value at internal constitutive substeps**.

If you want the **internal converged sampled value**, expose it as a material property in `CrystalPlasticityKalidindiVoceUpdate` (following your class's inheritance and naming conventions):

1. In the `.h`, declare `MaterialProperty<Real> & _gss_sat_output;`.
2. In the constructor initializer list, append `_gss_sat_output(declareProperty<Real>("voce_gss_sat"))`.
3. In `calculateStateVariableEvolutionRateComponent()`, after computing `_gss_sat`, assign `_gss_sat_output[_qp] = _gss_sat;`.
4. Recompile your application, then add an AuxVariable with `family = MONOMIAL, order = CONSTANT`; use `MaterialRealAux` with `property = voce_gss_sat`, `variable = gss_sat_internal`, and `execute_on = 'initial timestep_end'`. Output via `ElementAverageValue` if you want it in CSV.

Note that the property still reflects the converged recorded material state (depending on MOOSE update sequencing), **not all intermediate Newton/substep evaluations**. Definitive substep verification requires dedicated instrumentation or a unit test. Do not enable this AuxKernel until you implement the material property: otherwise the input fails because the property is absent.

## Admissibility caution

At positive but extremely low slip rate, the power law may yield `g_s <= g0=35 MPa` and cause the hardening ratio denominator to vanish or change sign. The sampled-step checks are not enough to guarantee admissibility at every internal iteration. If convergence fails, inspect the log and the material law before assuming the numerical time step is solely responsible.

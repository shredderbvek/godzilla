# MOOSE Voce final verification + Marin UMAT comparison setup

## What is included

- `voce_3pct_variable_sat_dt00125.i`: **new** 3% nonlinear anisotropic variable-saturation refinement (`dtmax=0.0125 s`).
- `voce_3pct_variable_sat_dt0025.i`: previous 0.025 s reference input copied for reproducibility.
- `voce_zero_slip_branch.i`: optional no-loading check of the zero-rate fallback.
- `slip_systems_FCC.txt`: verified 12-system FCC ordering grouped three per slip plane.
- `check_voce_3pct.py`: same ODE reconstruction checker used previously.
- `check_three_dt.py`: compares the 0.05 / 0.025 / 0.0125 s CSV results and writes `three_dt_summary.csv`.
- `probe_low_rate.py`: algebraic stress test of small positive slip rates and zero-rate discontinuity.
- `MARIN_COMPARISON_PROTOCOL.md`: source-to-source and Abaqus/MOOSE benchmark specification.
- `compare_marin_moose.py`: CSV stress–strain comparison for future equivalent runs.
- `umat_export_schema.csv`: blank UMAT export schema (header only), no invented results.

## Run the new MOOSE refinement

```bash
cd voce_final_verification
./run_remaining_tests.sh /home/ghostrobot96/projects/godzilla/godzilla-opt
```

The new CSV should be `voce_3pct_variable_sat_dt00125_out.csv`.

Copy the **actual** previously obtained `voce_3pct_variable_sat_dt005_out.csv` and `voce_3pct_variable_sat_dt0025_out.csv` into this directory before running the three-step checker. The script handles absent CSVs but cannot calculate a three-point convergence trend without them.

```bash
python3 check_three_dt.py
python3 probe_low_rate.py
```

Optional no-load branch run:

```bash
/home/ghostrobot96/projects/godzilla/godzilla-opt -i voce_zero_slip_branch.i
```

The zero-load test may report a tiny numerical slip rate rather than **exactly** zero. It therefore checks solver behavior and output, not the mathematical zero-rate branch with certainty.

## Interpretation and limitations

The expected `dtmax` refinement trend is approximately first order for **RK4-versus-MOOSE discrepancy computed with sampled global histories**. It is not guaranteed to be monotone because of adaptive time stepping and local substepping.

`probe_low_rate.py` prints the rate at which `gs = g0` and exports a diagnostic CSV. These results identify a mathematical domain issue in the *unregularized* power law; they do not prove the FE solver traverses that regime.

The Fortran `umat_umatht_3.f` source and its associated Abaqus input/parameter files are **not included** here. Actual UMAT-versus-MOOSE results require those source files and, preferably, a matching UMAT stress–strain/SDV export. Do not use a generic UMAT formula as a substitute for the active branch in the real code.

## Optional MOOSE-side controls for the subsequent Marin comparison

The following **candidate** reference inputs keep the same 3% load and 0.025 s cap; they do not claim to replicate the unknown UMAT settings:

- `marin_reference_constant_n1.i` — `n_gss=1`, `r=1`, constant saturation
- `marin_reference_isotropic_n1.i` — `n_gss=1`, `r=1`, rate-dependent saturation
- `marin_reference_plane_latent_n1.i` — `n_gss=1`, `r=1.4`, rate-dependent saturation

Run the applicable case only **after** inspecting the actual UMAT material parameters and q-matrix. The UMAT may implement a different stress update and hardening integration algorithm.

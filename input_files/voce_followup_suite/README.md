# Verification suite — nonlinear Voce hardening, FCC single crystal

These cases are derived directly from the previously working
`test_single_element_voce_n2_aniso_verify.i`.
They retain the same one-element geometry, 12 FCC slip systems, crystal orientation,
axial displacement (`0.0006*t` to 10 s), elastic constants, crystal-plasticity model,
flow parameters, and solver settings. Every case has **`n_gss = 2`** and **`r = 1.4`**.

**No MOOSE executable is included.** The supplied files and checker were checked
statically and with a CSV-format smoke test, not run with `godzillaApp` in this environment.

## Files

| Input file | Purpose | `dtmax` (s) | Saturation settings |
|---|---|---:|---|
| `voce_dtmax_0p200.i` | Time-step refinement A | 0.2 | Constant `g_s = 110 MPa` |
| `voce_dtmax_0p100.i` | Time-step refinement B | 0.1 | Constant |
| `voce_dtmax_0p050.i` | Time-step refinement C; reference for rate tests | 0.05 | Constant |
| `voce_dtmax_0p025.i` | Time-step refinement D | 0.025 | Constant |
| `voce_sat_rate_m0_control.i` | Check equivalence of rate branch with zero exponent | 0.05 | `is_gss_sat_constant=false`, `xm_gss=0`, `ao_sat=1e-5` s⁻¹ |
| `voce_sat_rate_m0025.i` | Rate sensitivity | 0.05 | `false`, `xm_gss=0.0025`, `ao_sat=1e-5` s⁻¹ |
| `voce_sat_rate_m0050.i` | Stronger rate sensitivity | 0.05 | `false`, `xm_gss=0.005`, `ao_sat=1e-5` s⁻¹ |
| `voce_sat_rate_m0050_ref1e3.i` | Reference-rate sensitivity | 0.05 | `false`, `xm_gss=0.005`, `ao_sat=1e-3` s⁻¹ |

`slip_systems_FCC.txt` is copied alongside the `.i` files. The supplied shell script
runs all eight cases and the Python script compares their CSV outputs.

## Run

Extract the archive, then enter the extracted directory. Run with the full path to
your compiled MOOSE executable:

```bash
cd voce_followup_suite
./run_voce_suite.sh /home/ghostrobot96/projects/godzilla/godzilla-opt
```

Or run a case separately (from this directory):

```bash
/home/ghostrobot96/projects/godzilla/godzilla-opt -i voce_dtmax_0p050.i
python3 check_voce_suite.py --allow-partial
```

If all eight CSVs exist, generate the complete comparison report with:

```bash
python3 check_voce_suite.py
```

The checker prints two tables and creates `voce_suite_summary.csv`. It requires
**only the Python standard library**. Each MOOSE case produces its own
`<input_stem>_out.csv`, Exodus output, and a `.log` file when run through the script.

## Test 1 — step-size refinement at constant saturation

The constitutive hardening law is

\[
\dot g^\alpha=h_0\left(\frac{g_s-g^\alpha}{g_s-g_0}\right)^2
\sum_\beta q^{\alpha\beta}|\dot\gamma^\beta|,
\qquad g_s=110\,\mathrm{MPa}.
\]

For constant saturation and initial `g_0 = 35 MPa`, its **exact continuous** solution
with accumulated interaction-weighted slip `Lambda_alpha` is

\[
g^\alpha(\Lambda_\alpha)
=110-\frac{75}{1+(190/75)\Lambda_\alpha}.
\]

The postprocessor `Lambda_plane_*` accumulates **global time-step endpoint**
weighted slip rates via implicit Euler. It is not the exact integrated slip history
if the material routine internally substeps. The Python checker reports:

- `dt_max_actual` (because `IterationAdaptiveDT` still varies the actual step),
- maximum absolute discrepancy to the continuous solution evaluated with the exported `Lambda`,
- nominal global-step backward-Euler residual,
- maximum spread among the three strengths on each FCC plane.

Inspect whether these errors trend downward as `dtmax` decreases. The rate of
convergence need not be a clean power law because the internal constitutive
substeps, global adaptive schedule, and slip-rate sampling also change.
**A decreasing plotted discrepancy is useful evidence, not independent proof of a
fully implicit local constitutive update.**

## Test 2 — rate-dependent saturation

Here the constitutive law uses

\[
g_s(\dot\Gamma)=\begin{cases}
110,&\text{if the constant branch is selected, or if }\dot\Gamma=0,\\
110\left(\dfrac{\dot\Gamma}{\dot\Gamma_{s0}}\right)^{m'},
&\text{otherwise},
\end{cases}
\qquad\dot\Gamma=\sum_{\beta=1}^{12}|\dot\gamma^\beta|.
\]

1. `m'=0` in the rate-dependent branch **must reproduce the constant-saturation
   branch** (same time-step cap, same initial conditions). This is a strong control
   of your boolean branch logic.
2. The `m'=0.0025` and `m'=0.005` cases should respond to the specified
   rate dependence. Compare per-plane slip resistances and axial stress at 10 s.
3. Holding `m'=0.005`, changing the reference rate from `1e-5` to `1e-3` s⁻¹
   should change `g_s` for nonzero slip rates.

Because `g_s` varies with slip rate, **do not** use the constant-saturation analytic
expression as the reference. Instead the checker reconstructs `g_s` from the
exported `Gamma_dot`, computes global-step backward-Euler residuals, and
independently integrates a **global-step BE approximation** using the exported
weighted slip increments and current `g_s`.

For the latter, at a saved step with `g_s` held at its endpoint value, let
`X = g_s - g_previous`, `A = h ΔLambda / (g_s-g_0)^2`. For `X>=0` and `A>=0`,

\[
g_{\mathrm{BE},\mathrm{next}}
=g_s-\frac{2X}{1+\sqrt{1+4AX}}.
\]

This is an exact algebraic solution of that **sampled-data BE subproblem**, but
not necessarily of MOOSE's internally substepped constitutive calculation.

### Parameter-admissibility warning

The original rate-dependent case with `xm_gss=1` and default
`ao_sat=5e10` s⁻¹ can make `g_s` much smaller than `g_0=35 MPa` at the slip
rates recorded in the earlier tests. Therefore, the demonstration cases use
**small positive exponents** and slip-rate references near the range of interest.
These are **numerical test parameters, not calibrated values for 316L or aluminum**.

The earlier simulation included slip rates as small as about `1.7e-59 s^-1`
in its initial elastic phase. A positive exponent can pull `g_s` downward at
vanishing positive slip rate. Our tests are chosen to keep `g_s > g_0` for
those *observed* rates, but they cannot guarantee the same bound for every
internal Newton iteration or constitutive substep. If a case fails, inspect
`<case>.log` and verify the admissibility of `g_s-g_0`; do **not** interpret
solver failure as a verification result. A physically motivated rate floor or
smoothing may be necessary for production modeling.

## Interpretation and limitations

- `slip_increment` is treated as **slip rate** following your MOOSE Kalidindi convention.
- All 12 slip systems are ordered in four blocks of three coplanar systems, so
  `i/3` is valid for this exact `slip_systems_FCC.txt` ordering.
- The analytical comparison assumes identical initial strengths and positive
  `g_s-g_0`. For nonlinear exponent 2 the exponentiation remains real, but
  unbounded evolution above saturation is a separate constitutive concern.
- For variable `g_s`, the checker computes the **expected formula from CSV rates**.
  Since `g_s` is local to the C++ function and not exported, it cannot directly
  check the value actually used in the constitutive update.
- No claim is made that these test files validate the model against experiments.
- For definitive local integration verification, add direct C++ unit tests for
  the hardening update or export the converged `g_s`, per-system hardening rate,
  and integrated absolute slip from the constitutive model.

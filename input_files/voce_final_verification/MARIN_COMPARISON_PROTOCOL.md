# Marin UMAT versus MOOSE Voce — comparison protocol

## Two different Marin-related sources

1. **Marin (2006), SAND2006-4170**, *On the Formulation of a Crystal Plasticity Model*, establishes a particular crystal plasticity stress update and a scalar rate-dependent saturation hardening law. This is **not automatically the same** as every code labeled "Marin UMAT".
2. In an earlier discussion, the user examined `umat_umatht_3.f`, whose `IntegrateHardening` routine used an active `kHARD_ANAL` branch. Previous inspection indicated a rate-dependent saturation `taus0*(SHRATE/gamss0)**xms`, interaction matrix `hardmtx`, and a special exponential hardening update. **Reinspect the exact Fortran source to verify these details**. Neither that UMAT source nor its input deck is included in this package, so a line-by-line or numerical Abaqus comparison cannot yet be claimed.

## MOOSE baseline already established

`CrystalPlasticityKalidindiVoceUpdate` uses a Kalidindi slip-rate law and generalized hardening:

- `Gamma_dot = sum_beta abs(gamma_dot_beta)`
- `gs = gs0*(Gamma_dot/Gamma_ref)**m` for positive rate; `gs0` at exactly zero rate if the constant-saturation switch is off
- `Lambda_dot_alpha = sum_beta q_alpha_beta * abs(gamma_dot_beta)`
- `g_dot_alpha = h0 * ((gs - g_alpha)/(gs - g0))**n * Lambda_dot_alpha` in the nonnegative-ratio domain
- `q=1` for coplanar pairs and `r` for noncoplanar pairs under the verified FCC file ordering

The MOOSE parent class `CrystalPlasticityKalidindiUpdate::updateStateVariables()` multiplies the evolution rate by `_substep_dt`, then adds it to the cached slip resistance from the previous constitutive substep. A predictor/corrector iteration and internal substepping are used. Verify against the exact MOOSE checkout used for the run.

## Stage 1 — constitutive hardening comparison (before stress comparison)

Match these quantities one by one in the actual UMAT and MOOSE source:

| Quantity | MOOSE name | UMAT (verify against actual source) |
|---|---|---|
| Initial resistance | `gss_initial` | Possibly `tausi`; `kappa` may use a different offset convention |
| Hardening modulus | `h` | `h0` |
| Saturation strength | `gss_sat_initial` | `taus0` |
| Saturation exponent | `xm_gss` | `xms` |
| Reference total slip rate | `ao_sat` | `gamss0` |
| Interaction matrix | plane-based `r` | `hardmtx` |
| Exponent of saturation ratio | `n_gss` | Is the exponent exactly 1, or configurable? |
| Hardening time integration | iterative backward-Euler-style substeps | inspect active `kHARD_ANAL` exact update |

**Do not equate `kappa` to `g_alpha` by name alone.** Inspect whether it stores total resistance, excess resistance above friction strength, or another hardening variable. Also verify whether UMAT uses `g_s-g0` or an effective saturation offset in the denominator.

### First apples-to-apples cases

1. Constant saturation, `n=1`, `r=1`, identical initial slip strengths. Compare scalar hardening against the exponential solution at a *prescribed identical total slip-rate history*. This suppresses crystal stress-update differences.
2. Constant saturation, `n=1`, `r=1.4`, **only if** the actual UMAT's `hardmtx` uses the same plane groupings and weights.
3. Rate-dependent saturation, `n=1`, same reference rate and exponent, using a shared prescribed slip-rate history. Compare UMAT's exact/exponential integration branch against MOOSE's iterative backward-Euler-style integration as `dt -> 0`.
4. Only use `n=2` if the UMAT actually supports the same exponent. Marin's original scalar law is effectively `n=1`.

The comparison must use a *common driving history* to distinguish hardening integration errors from changed slip kinetics. A full FE comparison follows only after this constitutive benchmark.

## Stage 2 — full single-crystal Abaqus/MOOSE comparison

- Same FCC slip-plane/direction file (including normalization and signs), same crystal orientation and Euler-angle convention
- Same single-crystal elastic stiffness and tensor component ordering
- Same flow rule reference slip rate and strain-rate exponent
- Same hardening constants, latent interactions and initial state
- Same boundary-condition kinematics, strain rate, specimen size and finite-strain convention
- Same strain measure and stress measure in output (e.g. Cauchy stress versus engineering strain); do not compare PK2 with Cauchy without transforming
- Same time-step ceiling and progressively tighter constitutive tolerances
- Same averaging or element/integration-point extraction method

Output stress, strain, all slip resistances and individual signed slip rates at matched times. The `umat_export_schema.csv` is a **header-only** template; fill it using the actual Abaqus UMAT's output mapping, not an assumed SDV index.

Compare curves with:

```bash
python3 compare_marin_moose.py \
 --moose-csv path/to/moose_out.csv \
 --umat-csv path/to/umat_export.csv
```

The comparator interpolates MOOSE stress onto the UMAT strain samples within the overlapping strain interval and reports stress differences. It does not claim equivalence of the constitutive laws.

## Remaining MOOSE verification gates

- `dtmax=0.0125` at 3% strain with `r=1.4`, `n=2`, `m'=0.005` (main test)
- Test the **exact zero-slip branch** under zero displacement (optional baseline)
- Algebraically sweep positive slip rates down to extremely small values to identify when `gs <= g0`, and check the discontinuity at exactly zero rate
- For robust deployed models, consider a physically justified low-rate regularization and explicit admissibility guard, which will require source-code changes and must be calibrated/validated independently

## Important distinctions

- `g_s_formula_saved` in the input is **reconstructed** from exported converged global-step slip rates, not a direct trace of every local constitutive iteration.
- A decreasing discrepancy against RK4 with linearly interpolated **saved** rates is a consistency check, not a proof that the MOOSE local integrator matches an independently imposed continuous rate history.
- Comparisons against Marin (2006) report predictions do not replace direct comparison to the actual Fortran UMAT update algorithm.

## Sources

- Marin, E. B. (2006), *On the Formulation of a Crystal Plasticity Model*, SAND2006-4170.
- MOOSE source: `CrystalPlasticityKalidindiUpdate.C`, `calculateSlipRate`, `calculateStateVariableEvolutionRateComponent`, and `updateStateVariables`.

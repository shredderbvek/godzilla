# Nonlinear Voce material-point verification (n = 2)

These inputs are derived from the previously working `test_single_element_voce_aniso_analytic_verify.i` supplied in this conversation. They use the same single 3-D finite element, FCC slip-system definition, loading to 0.6% engineering strain at t=10 s, elastic constants, and flow rule. Both enable `is_gss_sat_constant = true`, `gss_initial = 35`, `gss_sat_initial = 110`, `h = 190`, and `n_gss = 2`. `r` is either 1 or 1.4.

## Governing equations

Define the interaction-weighted accumulated slip

\[
\Lambda^\alpha(t) = \int_0^t \sum_{\beta=1}^{12} q^{\alpha\beta}|\dot\gamma^\beta| \, d\tau.
\]

At fixed saturation strength, the hardening ODE is

\[
\frac{dg^\alpha}{d\Lambda^\alpha} = h_0\left(\frac{g_s-g^\alpha}{g_s-g_0}\right)^n.
\]

With n=2, g(0)=g0, the exact trajectory is

\[
g^\alpha = g_s - \frac{g_s-g_0}{1 + [h_0/(g_s-g_0)]\Lambda^\alpha}
= 110 - \frac{75}{1+(190/75)\Lambda^\alpha}.
\]

For comparison the n=1 trajectory at the same Lambda is

\[
g^\alpha_{n=1}=110-75\exp[-(190/75)\Lambda^\alpha].
\]

For r=1, all Lambda^alpha equal Gamma=integral sum |slip rate| dt. For r=1.4 and FCC systems grouped by three on each plane, there are four distinct Lambda_plane_p values, with weighted rate 1.4 Gamma_dot - 0.4 Gamma_dot_plane_p.

## Files

* `test_single_element_voce_n2_iso_verify.i`: n=2, r=1.0.
* `test_single_element_voce_n2_aniso_verify.i`: n=2, r=1.4.
* `verify_voce_n2.py`: read the resulting CSV, compare the output to the n=2 exact trajectory and n=1 reference, check the strengths of coplanar slip systems, and report an approximate discrete BE residual.
* `slip_systems_FCC.txt`: the FCC slip-system file from the conversation.

## Run

Execute from the directory that contains all files:

```bash
./godzilla-opt -i test_single_element_voce_n2_iso_verify.i
./godzilla-opt -i test_single_element_voce_n2_aniso_verify.i
python3 verify_voce_n2.py \
  test_single_element_voce_n2_iso_verify_out.csv \
  test_single_element_voce_n2_aniso_verify_out.csv
```

Use the path to your executable as appropriate.

## Interpretation

1. Check that all 12 strengths agree in the r=1 test.
2. For r=1.4, check that each coplanar set (1-3, 4-6, 7-9, 10-12) has identical strength, and different planes generally differ.
3. Compare numerical strengths to the n=2 exact trajectory **at the calculated Lambda**, not at identical time alone.
4. The n=2 reference should fit substantially better than the n=1 reference if the exponent was applied correctly.
5. Repeat with a smaller `dtmax` for time-step convergence; the analytical comparison uses a globally sampled endpoint-rate quadrature. This is not a proof that the internal CP integrator uses backward Euler exactly.
6. If the difference between n=1 and n=2 is too small at 0.6% strain, increase the prescribed displacement from `function = '0.0006 * t'` to `function = '0.003 * t'` (3% at t=10), **after** first establishing that the baseline case works. Recheck solver and integration convergence.

Important: the current C++ power law uses `abs(h_ratio)` for n != 1. The reference derived above assumes 35 <= g^alpha < 110; it does not validate the choice of sign or recovery behavior for g above saturation. Also, this verification treats saturation as constant; rate-dependent saturation needs its own test.

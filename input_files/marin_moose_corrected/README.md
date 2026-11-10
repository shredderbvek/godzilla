# Matched MAT1_GRN1 single-element comparison

## Reference source and orientation

`texture.txti` original first row (Kocks degrees): (275.27, 80.07, 303.66). The target **Bunge** angles for the active MOOSE CP rotation are **(5.269999999999982, 80.07, 146.33999999999997)** degrees, not (185.27,80.07,146.34).

For the specific Marin `AnglesToRotMatrix` and MOOSE `RotationTensor` (the active transpose is used by ComputeElasticityTensorCP), the converted Bunge angles generate the same crystal-to-sample matrix:

```
-0.8376018 -0.5387372 +0.0904732
+0.0187260 -0.1938349 -0.9808554
+0.5459602 -0.8198721 +0.1724449
```

Max abs rotation-matrix difference computed in Python: 2.64e-16.

**Important:** The supplied historical `texture.txto` reports `(255.98, 78.44, 138.19)` for grain 1, and your original `texture.txti` contains 500 different orientations. `MAT1_GRN1` only sets material/grain indices; the actual selection depends on the UMAT `kODF` configuration and run context. To keep this benchmark deterministic, these reference decks use an orientation file with 500 repeated copies of the FIRST desired orientation `(275.27,80.07,303.66)` (Kocks). Check the fresh `texture.txto` after the Abaqus run confirms this orientation.

## Cases

- `baseline`: unirradiated material parameters from `fcc_baseline.sx` copied as `Mat1/fcc.sx`: slip reference rate 0.001/s, m = 0.05, C11=185000, C12=125000, C44=118000 MPa, h0=190, g0=35, gs=110, xms=0, kappa0=35 MPa.
- `active_5dpa`: active original `fcc.sx`: same stiffness and kinetics, h0=190, g0=85.53, gs=160.53, xms=0, kappa0=85.53 MPa.

Both: `r=1`, `n_gss=1`, constant saturation and 5% X strain over 1s. One 1x1x1 mm C3D8/HEX8 with rollers on x=-0.5, y=-0.5, z=0 and 0.05 mm loading x=+0.5. **No CZM**.

Corrected a prior input issue: the nine stiffness values now follow MOOSE `symmetric9` order as `185000 125000 125000 185000 125000 185000 118000 118000 118000`. A previous deck erroneously had `104374` for C2233.

The `slip_systems_FCC_MAT1.txt` file was copied in the exact **12-system order and signs** of the `fcc.sx` slip-mode block.

## Run MOOSE

From a case directory:
```
/home/ghostrobot96/projects/godzilla/godzilla-opt -i moose_baseline.i
# or
/home/ghostrobot96/projects/godzilla/godzilla-opt -i moose_active_5dpa.i
```
The files record Sxx, right-side displacement, numerical GSS and 12 slip rates.

## Run Abaqus

Use the desired case directory and your existing compiled Fortran UMAT toolchain, for example:
```
abaqus job=abaqus_baseline input=abaqus_baseline.inp user=/path/to/umat_czm.f interactive
# or in active_5dpa directory:
abaqus job=abaqus_active_5dpa input=abaqus_active_5dpa.inp user=/path/to/umat_czm.f interactive
```

**UMAT file paths:** This archive puts `Mat1/test.xtali`, `Mat1/fcc.sx`, and `Mat1/texture.txti` inside each case. Your UMAT runtime (`filePath`, `fileRoot`) must be configured to read the matching case Mat1 folder. The UMAT also references external code/includes (`params_xtal.inc`, `numkind`, any required vertex files). They are not included and need to remain accessible from your existing simulation setup. Check the newly generated UMAT `.xtale`/`.txto` files rather than reusing historical output. `MAT1_GRN1` constants `768., 1.` are retained in the Abaqus deck; do not interpret them as actual material parameters.

## Caveats

- Constitutive algorithms differ (Marin UMAT uses its own integration and slip-rate bounds; MOOSE uses `CrystalPlasticityKalidindiVoceUpdate` and its parent substep integration).
- These decks align initial material and geometry but are not numerical proof of equivalence. Compare elastic response first, then slip resistance and slip rate.
- MOOSE standalone execution against your local `godzilla-opt` and Abaqus was not possible here.

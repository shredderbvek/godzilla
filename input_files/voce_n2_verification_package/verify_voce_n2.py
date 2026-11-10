#!/usr/bin/env python3
"""Check n_gss=2 constant-saturation Voce CSV outputs (isotropic or anisotropic).

The exact formula g=gs-(gs-g0)/(1+(h/(gs-g0))*Lambda) is exact
when Lambda is the true accumulated interaction-weighted slip. The
CSV Lambda values use global-step endpoint quadrature, so discrepancies
need not represent constitutive errors.

Usage:
  python3 verify_voce_n2.py test_single_element_voce_n2_iso_verify_out.csv
  python3 verify_voce_n2.py test_single_element_voce_n2_aniso_verify_out.csv
"""
import argparse
import csv
import math
from pathlib import Path

G0 = 35.0
GS = 110.0
H = 190.0
DELTA = GS - G0

def g_exact(lam):
    return GS - DELTA / (1.0 + (H / DELTA) * lam)

def g_linear_voce(lam):
    return GS - DELTA * math.exp(-(H / DELTA) * lam)

def read_data(csv_path):
    with csv_path.open(newline='') as handle:
        reader = csv.DictReader(handle)
        if not reader.fieldnames:
            raise ValueError('Missing CSV column headers')
        names = set(reader.fieldnames)
        required = {'time', 'Gamma_abs'}
        for p in range(1, 5):
            required.add(f'Lambda_plane_{p}')
            for j in range(3*(p-1)+1, 3*p+1):
                required.add(f'gss_{j:02}_num')
        missing = sorted(required - names)
        if missing:
            raise ValueError('Missing expected columns: ' + ', '.join(missing))
        rows = [{k: float(v) for k, v in raw.items() if v not in (None, '')}
                for raw in reader]
    if not rows:
        raise ValueError('CSV has no data rows')
    if any(b['time'] <= a['time'] for a,b in zip(rows, rows[1:])):
        raise ValueError('Time must increase strictly')
    return rows

def analyze(path):
    rows=read_data(path)
    final=rows[-1]
    final_time=final['time']
    print(f'\nFILE: {path.name}')
    print(f'Rows: {len(rows)}; t_final = {final_time:.7g} s; Gamma = {final["Gamma_abs"]:.8g}')
    print('Plane   Lambda_final     MOOSE_final      Exact(n=2)    Final_error     Max_abs_error    Coplanar_spread')
    print('-'*103)
    for p in range(1,5):
        gnames=[f'gss_{i:02}_num' for i in range(3*(p-1)+1,3*p+1)]
        lkey=f'Lambda_plane_{p}'
        errs=[row[gnames[0]] - g_exact(row[lkey]) for row in rows]
        spreads=[max(row[k] for k in gnames)-min(row[k] for k in gnames) for row in rows]
        lam=final[lkey]
        g=final[gnames[0]]
        pred=g_exact(lam)
        print(f'{p:5d}   {lam:12.8f}   {g:14.8f}   {pred:12.8f}   {g-pred:+12.8f}   {max(map(abs,errs)):13.8f}   {max(spreads):15.3e}')
        print(f'        final |error vs n=1 reference|: {abs(g-g_linear_voce(lam)):.7f} MPa')
        print(f'        n=1 vs n=2 reference separation at this Lambda: {g_linear_voce(lam)-pred:+.7f} MPa')
        # Nominal n=2 backward-Euler hardening residual on exported global steps.
        # This is diagnostic, not exact when the CP update internally substeps.
        be_residuals = []
        for before, after in zip(rows, rows[1:]):
            dlambda = after[lkey] - before[lkey]
            rhs = H * dlambda * ((GS - after[gnames[0]]) / DELTA)**2
            be_residuals.append((after[gnames[0]]-before[gnames[0]]) - rhs)
        if be_residuals:
            print(f'        max |global-step n=2 BE residual|: {max(map(abs,be_residuals)):.8f} MPa')
    abs_diffs=[]
    for row in rows:
        for p in range(1,5):
            keys=[f'gss_{i:02}_num' for i in range(3*(p-1)+1,3*p+1)]
            abs_diffs.append(abs(row[keys[0]]-g_exact(row[f'Lambda_plane_{p}'])))
    print(f'Max reference discrepancy across planes and saved times: {max(abs_diffs):.8f} MPa')
    print('NOTE: This is a consistency check using sampled Lambda, not proof of an exact local integration scheme.')

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('csv_files', nargs='+',type=Path)
    args=parser.parse_args()
    for path in args.csv_files:
        analyze(path)

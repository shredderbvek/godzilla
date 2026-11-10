#!/usr/bin/env python3
"""Compare stress/strength curves from user-exported MOOSE and Abaqus UMAT CSVs.

No claim of physical model equivalence. See MARIN_COMPARISON_PROTOCOL.md.
UMAT CSV requires columns engineering_strain, axial_cauchy_stress_MPa by default.
Optional slip-system resistance columns: gss_01_MPa ... gss_12_MPa.
"""
import argparse
import csv
import math
from pathlib import Path


def read_rows(filename, x_name, y_name):
    with open(filename, newline='') as f:
        reader=csv.DictReader(f)
        headers=set(reader.fieldnames or [])
        required={x_name,y_name}
        if not required.issubset(headers):
            raise ValueError(f'{filename}: missing {sorted(required-headers)}; available={sorted(headers)}')
        rows=[]
        for row in reader:
            try: x=float(row[x_name]); y=float(row[y_name])
            except (TypeError, ValueError): continue
            if math.isfinite(x) and math.isfinite(y): rows.append((x,y,row))
    if len(rows)<2: raise ValueError(f'Not enough finite data points in {filename}')
    rows.sort(key=lambda v:v[0])
    for a,b in zip(rows,rows[1:]):
        if not a[0]<b[0]: raise ValueError(f'{filename}: duplicate/non-increasing strain {a[0]}')
    return rows


def interp(rows,x):
    lo=0;hi=len(rows)-1
    if x<rows[0][0] or x>rows[-1][0]:return None
    if x==rows[-1][0]:return rows[-1][1]
    while hi-lo>1:
        mid=(hi+lo)//2
        if rows[mid][0]<=x:lo=mid
        else:hi=mid
    x0,y0,_=rows[lo];x1,y1,_=rows[hi]
    return y0+(y1-y0)*(x-x0)/(x1-x0)


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--moose-csv',required=True)
    ap.add_argument('--umat-csv',required=True)
    ap.add_argument('--moose-strain',default='strain_zz')
    ap.add_argument('--moose-stress',default='stress_zz')
    ap.add_argument('--umat-strain',default='engineering_strain')
    ap.add_argument('--umat-stress',default='axial_cauchy_stress_MPa')
    ap.add_argument('--out',default='marin_moose_overlay.csv')
    args=ap.parse_args()
    a=read_rows(args.moose_csv,args.moose_strain,args.moose_stress)
    b=read_rows(args.umat_csv,args.umat_strain,args.umat_stress)
    overlap=[]
    for e,s,_ in b:
        sm=interp(a,e)
        if sm is not None: overlap.append((e,sm,s,sm-s))
    if not overlap: raise ValueError('No common strain window to compare')
    dest=Path(args.out)
    with dest.open('w',newline='') as f:
        w=csv.writer(f)
        w.writerow(['engineering_strain','MOOSE_stress_MPa','UMAT_stress_MPa','MOOSE_minus_UMAT_MPa'])
        w.writerows(overlap)
    errs=[t[3] for t in overlap]
    rmse=math.sqrt(sum(x*x for x in errs)/len(errs))
    print(f'Compared {len(overlap)} UMAT samples over shared engineering strain range '
          f'{overlap[0][0]:.8g} .. {overlap[-1][0]:.8g}')
    print(f'RMSE={rmse:.9g} MPa; max|delta|={max(map(abs,errs)):.9g} MPa; '
          f'final delta={errs[-1]:+.9g} MPa')
    print('Output:',dest)
    print('CAUTION: Only interpret this as material-model comparison after matching '
          'stress measure, orientation, flow law, kinematics, parameters, units, and time history.')

if __name__=='__main__':main()

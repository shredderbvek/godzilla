#!/usr/bin/env python3
"""Algebraic audit of g_s = g_s0 * (Gamma_dot/Gamma_ref)^m.

This probes near-zero total slip rates without relying on finite-element solver tolerances.
"""
import argparse
import csv
import math
from pathlib import Path

G_S0, G0, GAMMA_REF = 110.0, 35.0, 1e-5
EXPONENTS=(0.005, 0.05, 0.2)


def gs(rate,m):
    if rate < 0: raise ValueError('Total absolute slip rate cannot be negative')
    return G_S0 if rate==0 else G_S0*pow(rate/GAMMA_REF,m)


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--output', default='low_rate_sweep.csv')
    args=ap.parse_args()
    rates = [0.0] + sorted({10.0**x for x in range(-300,0,5)} |
                          {1e-120,1e-110,1e-106,1e-105,3.428244898446326e-105,
                           1e-104,1e-102,1e-15,1e-8,1e-5,1e-3})
    rows=[]
    for m in EXPONENTS:
        threshold = GAMMA_REF*pow(G0/G_S0,1/m)
        print(f'm={m:.4g}: g_s=g0 when Gamma_dot≈{threshold:.12e} s^-1')
        print(f'  at Gamma_dot=0 exactly: gs={gs(0,m):.9g}; '
              f'as Gamma_dot→0+ : gs→0 for any m>0')
        for rate in rates:
            s=gs(rate,m)
            rows.append({'m':m,'Gamma_dot_s-1':rate,'g_s_MPa':s,
                         'g_s_minus_g0_MPa':s-G0,
                         'admissible_g_s_gt_g0': int(s>G0)})
    out=Path(args.output)
    with out.open('w', newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
    print(f'Wrote {out}')
    print('This script checks the mathematical domain of the law; it does not test MOOSE state iteration.')
    print('The zero-rate fallback is discontinuous and cannot be fixed solely by smaller timesteps.')


if __name__=='__main__': main()

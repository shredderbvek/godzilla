#!/usr/bin/env python3
"""Check 3%-strain variable-saturation Voce time-step refinement.

Requires CSV results from the 0.05, 0.025, and 0.0125 s runs.
References use *saved endpoint* slip-rate histories, not local constitutive substeps.
"""
import csv
import math
from pathlib import Path
from check_voce_3pct import analyze

HERE = Path(__file__).resolve().parent
CASE_FILES = [
    ('0.05', HERE / 'voce_3pct_variable_sat_dt005_out.csv'),
    ('0.025', HERE / 'voce_3pct_variable_sat_dt0025_out.csv'),
    ('0.0125', HERE / 'voce_3pct_variable_sat_dt00125_out.csv'),
]


def main():
    summaries = []
    for label, path in CASE_FILES:
        if not path.is_file():
            print(f'MISSING: {path.name} (run MOOSE or copy your existing CSV here)')
            continue
        record = analyze(path)
        worst_err = max(p['max_error_RK4'] for p in record['planes'])
        worst_res = max(p['max_global_BE_residual'] for p in record['planes'])
        s = {
            'dtmax_s': float(label), 'rows': record['rows'],
            'stress_final_MPa': record['stress_final'],
            'strain_final': record['strain_final'],
            'g_s_min_saved_MPa': record['gs_min_saved'],
            'g_s_max_saved_MPa': record['gs_max_saved'],
            'g_s_final_saved_MPa': record['gs_final_saved'],
            'coplanar_spread_MPa': record['coplanar_spread'],
            'max_RK4_discrepancy_MPa': worst_err,
            'max_global_BE_residual_MPa': worst_res,
            **{f'g_plane_{p["plane"]}_final_MPa': p['g_MOOSE'] for p in record['planes']},
        }
        summaries.append(s)
        print(f'\ndtmax={label}: {record["rows"]-1} global steps; '
              f'strain={s["strain_final"]:.7g}; stress={s["stress_final_MPa"]:.8f} MPa')
        print(f'  max reconstructed RK4 error={worst_err:.9g} MPa; '
              f'max global BE residual={worst_res:.9g} MPa')
        print(f'  saved gs range=[{s["g_s_min_saved_MPa"]:.7g}, '
              f'{s["g_s_max_saved_MPa"]:.7g}] MPa, coplanar spread={s["coplanar_spread_MPa"]:.2e} MPa')
    if summaries:
        out = HERE / 'three_dt_summary.csv'
        with out.open('w',newline='') as f:
            writer = csv.DictWriter(f, fieldnames=list(summaries[0])); writer.writeheader(); writer.writerows(summaries)
        print(f'\nWrote {out}')
    for coarse, fine in zip(summaries, summaries[1:]):
        if not math.isclose(coarse['dtmax_s']/fine['dtmax_s'],2.,abs_tol=1e-7):
            print('\nSkipped convergence-order estimate: missing intermediate dtmax result')
            continue
        E0,E1=coarse['max_RK4_discrepancy_MPa'],fine['max_RK4_discrepancy_MPa']
        R0,R1=coarse['max_global_BE_residual_MPa'],fine['max_global_BE_residual_MPa']
        pE=math.log(E0/E1,2) if E0>0 and E1>0 else float('nan')
        pR=math.log(R0/R1,2) if R0>0 and R1>0 else float('nan')
        print(f'\n{coarse["dtmax_s"]} -> {fine["dtmax_s"]}: '
              f'error ratio={E0/E1:.4f}, p_error={pE:.3f}, '
              f'BE residual ratio={R0/R1:.4f}, p_residual={pR:.3f}')
        print(f'  final stress delta = {fine["stress_final_MPa"]-coarse["stress_final_MPa"]:+.8f} MPa')
        for i in range(1,5):
            key=f'g_plane_{i}_final_MPa'
            print(f'  plane {i} strength delta = {fine[key]-coarse[key]:+.8f} MPa')
    print('\nCAUTION: The RK4 reference interpolates exported global-step rates. It does not recover '
          'the locally substepped history, so these are consistency metrics, not exact solver errors.')


if __name__=='__main__':
    main()

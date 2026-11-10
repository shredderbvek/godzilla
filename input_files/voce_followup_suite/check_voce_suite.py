#!/usr/bin/env python3
"""Analyze MOOSE n=2, r=1.4 Voce convergence and variable saturation tests.

Uses ONLY Python standard library. Run after run_voce_suite.sh.
Checks:
- slip-rate summation, per-plane interaction weights, equal coplanar strengths
- constant g_sat: exact n=2 solution evaluated at exported Lambda
- time-step refinement: actual maximal dt and errors vs analytic reference
- variable g_sat: computed from exported total slip rates and rate scaling
- global-step BE residuals (diagnostics ONLY; substeps and endpoint quadrature matter)
- m=0 dynamic-branch control vs explicit constant saturation branch
Outputs voce_suite_summary.csv (does not modify simulation results).
"""
import argparse
import csv
import math
import sys
from pathlib import Path

G0, GS0, H, N, Q = 35.0, 110.0, 190.0, 2.0, 1.4
DELTA = GS0 - G0
DT_TESTS = [
    ('voce_dtmax_0p200', 0.2),
    ('voce_dtmax_0p100', 0.1),
    ('voce_dtmax_0p050', 0.05),
    ('voce_dtmax_0p025', 0.025),
]
RATE_TESTS = [
    ('voce_sat_rate_m0_control', 0.0, 1e-5),
    ('voce_sat_rate_m0025', 0.0025, 1e-5),
    ('voce_sat_rate_m0050', 0.005, 1e-5),
    ('voce_sat_rate_m0050_ref1e3', 0.005, 1e-3),
]
ALL = [name for name, _ in DT_TESTS] + [name for name, _, _ in RATE_TESTS]

def read_csv(path):
    with path.open(newline='') as fd:
        reader = csv.DictReader(fd)
        keys = set(reader.fieldnames or [])
        wanted = {'time', 'Gamma_dot', 'Gamma_abs', 'stress_zz', 'strain_zz'}
        for i in range(1, 13):
            wanted.update((f'gss_{i:02}_num', f'slip_rate_{i:02}' if f'slip_rate_{i:02}' in keys else 'Gamma_dot'))
        for p in range(1, 5):
            wanted.update((f'Lambda_plane_{p}',f'Lambda_plane_{p}_dot'))
        # slip_rate_XX exists as an AuxVariable, not necessarily as CSV postprocessor:
        # the existing input CSV exports only total/plane rates; skip individual
        # slip-rate columns unless the caller separately adds postprocessors.
        wanted = {x for x in wanted if not x.startswith('slip_rate_')}
        missing = sorted(wanted-keys)
        if missing:
            raise ValueError(f'{path.name} missing expected columns: {", ".join(missing)}')
        rows = [{key:float(value) for key,value in row.items() if value not in ('',None)} for row in reader]
    if len(rows)<2:
        raise ValueError(f'{path.name}: need at least 2 rows')
    if any(not math.isfinite(value) for row in rows for value in row.values()):
        raise ValueError(f'{path.name}: nonfinite value detected')
    if any(y['time']<=x['time'] for x,y in zip(rows, rows[1:])):
        raise ValueError(f'{path.name}: times must strictly increase')
    return rows

def g_exact(lmbda):
    return GS0-DELTA/(1.0+(H/DELTA)*lmbda)

def g_saturation(rate,m,rate_ref):
    return GS0 if rate<=0.0 else GS0*(rate/rate_ref)**m

def analyze(name, rows, m=None, rate_ref=None):
    variable=(m is not None)
    sat=[g_saturation(row['Gamma_dot'],m,rate_ref) if variable else GS0 for row in rows]
    max_spread=0.0
    max_be=0.0
    max_exact=0.0
    max_reconstructed_BE_error=0.0
    final_reconstructed_BE_error=0.0
    final_errors=[]
    for p in range(1,5):
        keys=[f'gss_{i:02}_num' for i in range(3*(p-1)+1,3*p+1)]
        for row in rows:
            strengths=[row[k] for k in keys]
            max_spread=max(max_spread,max(strengths)-min(strengths))
            if not variable:
                max_exact=max(max_exact, abs(row[keys[0]]-g_exact(row[f'Lambda_plane_{p}'])))
        be_reconstructed=rows[0][keys[0]]
        for i in range(1,len(rows)):
            before,after=rows[i-1],rows[i]
            dL = after[f'Lambda_plane_{p}']-before[f'Lambda_plane_{p}']
            if dL<-1e-12:
                raise ValueError(f'{name}: negative interaction-weighted accumulated slip on plane {p}')
            denom=sat[i]-G0
            if denom>0.0 and dL>=0.0:
                A=H*dL/(denom**2)
                xprev=sat[i]-be_reconstructed
                if xprev>=0.0:
                    xnew=2.0*xprev/(1.0+math.sqrt(1.0+4.0*A*xprev))
                    be_reconstructed=sat[i]-xnew
                    max_reconstructed_BE_error=max(max_reconstructed_BE_error,abs(be_reconstructed-after[keys[0]]))
                    if i==len(rows)-1:
                        final_reconstructed_BE_error=max(final_reconstructed_BE_error, abs(be_reconstructed-after[keys[0]]))
            if abs(denom)>1e-15:
                residual=(after[keys[0]]-before[keys[0]])-H*dL*((sat[i]-after[keys[0]])/denom)**2
                max_be=max(max_be,abs(residual))
        if not variable:
            final_errors.append(rows[-1][keys[0]]-g_exact(rows[-1][f'Lambda_plane_{p}']))
    dts=[y['time']-x['time'] for x,y in zip(rows, rows[1:])]
    last=rows[-1]
    out={
        'name':name,
        'rows':len(rows),
        't_final':last['time'],
        'dt_max_actual':max(dts),
        'dt_min_actual':min(dts),
        'Gamma_final':last['Gamma_abs'],
        'stress_final_MPa':last['stress_zz'],
        'strain_final':last['strain_zz'],
        'max_coplanar_spread_MPa':max_spread,
        'max_global_BE_residual_MPa':max_be,
        'max_BE_reconstruction_error_MPa':max_reconstructed_BE_error,
        'final_BE_reconstruction_error_MPa':final_reconstructed_BE_error,
        'max_exact_error_MPa':max_exact if not variable else '',
        'max_final_exact_error_MPa':max(map(abs,final_errors)) if not variable else '',
        'gs_min_all_MPa':min(sat),
        'gs_final_MPa':sat[-1],
        'gs_max_all_MPa':max(sat),
        'g_plane_final_MPa':' '.join(f'{last[f"gss_{i:02}_num"]:.9g}' for i in (1,4,7,10))
    }
    active=[v for i,v in enumerate(sat) if rows[i]['Gamma_dot']>=1e-5]
    out['gs_min_active_MPa'] = min(active) if active else ''
    return out

def fmt(x, digits=7):
    return f'{x:.{digits}g}' if isinstance(x,(float,int)) else str(x)

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--directory',type=Path,default=Path(__file__).resolve().parent,
                        help='Directory with MOOSE output CSVs')
    parser.add_argument('--allow-partial',action='store_true',
                        help='Analyze whichever test results are present (else require all eight)')
    args=parser.parse_args()
    directory=args.directory
    paths={name:directory/f'{name}_out.csv' for name in ALL}
    missing=[name for name,path in paths.items() if not path.exists()]
    if missing and not args.allow_partial:
        print('Missing simulation CSV files. Run ./run_voce_suite.sh /path/to/godzilla-opt first:')
        for name in missing: print('  '+paths[name].name)
        return 2
    all_rows={}
    metrics={}
    for name in ALL:
        if not paths[name].exists():continue
        rows=read_csv(paths[name])
        all_rows[name]=rows
        rate_settings=next(((m,ref) for case,m,ref in RATE_TESTS if case==name),None)
        metrics[name]=analyze(name,rows,*(rate_settings or (None,None)))
    if not metrics:
        print('No CSVs found')
        return 2

    print('\nI. TIME-STEP REFINEMENT: n=2, r=1.4, constant saturation')
    print('Case                 dt ceiling   max actual dt  steps  max|g-g_exact|  max|global BE res|  max coplanar spread')
    for name, cap in DT_TESTS:
        if name not in metrics:continue
        x=metrics[name]
        print(f'{name:22} {cap:10.3f} {x["dt_max_actual"]:14.6f} {x["rows"]-1:6d} '
              f'{x["max_exact_error_MPa"]:15.8f} {x["max_global_BE_residual_MPa"]:19.8f} '
              f'{x["max_coplanar_spread_MPa"]:19.3e}')
        if x['dt_max_actual']>cap*(1+1e-5):
            print(f'  WARNING: measured dt exceeds dtmax={cap}. Check TimeStepper.')

    print('\nII. RATE-DEPENDENT SATURATION: n=2, r=1.4, dtmax=0.05')
    print('Case                           gs_min(all)  gs_min(active) gs_final   g1_final    stress_final   max|BE reconstruction error|')
    for name,m,ref in RATE_TESTS:
        if name not in metrics:continue
        x=metrics[name]
        print(f'{name:31} {x["gs_min_all_MPa"]:11.4f} '
              f'{fmt(x["gs_min_active_MPa"]):>14} {x["gs_final_MPa"]:9.4f} '
              f'{all_rows[name][-1]["gss_01_num"]:11.6f} '
              f'{x["stress_final_MPa"]:13.6f} {x["max_BE_reconstruction_error_MPa"]:19.8f}')
        if x['gs_min_all_MPa']<=G0:
            print('  WARNING: gs <= initial resistance g0 at a saved time. Formula may be inadmissible.')
    if 'voce_dtmax_0p050' in all_rows and 'voce_sat_rate_m0_control' in all_rows:
        ref=all_rows['voce_dtmax_0p050'][-1]
        ctrl=all_rows['voce_sat_rate_m0_control'][-1]
        maxg=max(abs(ref[f'gss_{i:02}_num']-ctrl[f'gss_{i:02}_num']) for i in range(1,13))
        print(f'\nZero-exponent branch control vs constant branch at t=10:')
        print(f'  max final |delta g|: {maxg:.6e} MPa; '
              f'|delta stress|: {abs(ref["stress_zz"]-ctrl["stress_zz"]):.6e} MPa')
        if maxg>1e-5:
            print('  WARNING: m=0 dynamic-branch control does not match constant branch closely.')
    if 'voce_dtmax_0p050' in all_rows:
        ref=all_rows['voce_dtmax_0p050'][-1]
        print('\nEnd-point sensitivity relative to constant-saturation baseline:')
        for name,m,rate_ref in RATE_TESTS:
            if name not in all_rows:continue
            row=all_rows[name][-1]
            print(f'  {name:30} delta_g1={row["gss_01_num"]-ref["gss_01_num"]:+.8f} MPa; '
                  f'delta_sigma_zz={row["stress_zz"]-ref["stress_zz"]:+.8f} MPa')
    print('\nIII. LIMITATIONS')
    print('  - Lambda is integrated from exported endpoint slip rates; internal CP substeps are not visible.')
    print('  - Time-step refinement tests convergence of the composite simulation + sampled-rate diagnostic.')
    print('  - For varying gs, no constant-gs closed-form analytical solution applies.')
    print('  - Global-step BE residuals do NOT prove the constitutive integrator uses BE.')
    print('  - gs here is reconstructed from exported Gamma_dot and the prescribed formula,')
    print('    not a material property directly exported by the constitutive C++ class.')
    print('  - The material may see smaller slip rates at internal iterations than the saved CSV rates.')
    outfile=directory/'voce_suite_summary.csv'
    keys=list(next(iter(metrics.values())).keys())
    with outfile.open('w',newline='') as fd:
        wr=csv.DictWriter(fd,fieldnames=keys)
        wr.writeheader()
        for name in ALL:
            if name in metrics: wr.writerow(metrics[name])
    print(f'\nWrote {outfile}')
    return 0

if __name__=='__main__':
    try: sys.exit(main())
    except (ValueError,OSError,ZeroDivisionError) as ex:
        print(f'ERROR: {ex}',file=sys.stderr)
        sys.exit(1)

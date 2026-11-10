#!/usr/bin/env python3
"""Compare 3% variable-saturation Voce runs using exported MOOSE histories.

Two independent *postprocessed-history* integrations are provided:
  - RK4 with piecewise-linearly interpolated endpoint slip rates
  - Global backward Euler with endpoint saturation and Lambda-dot
They are NOT exact references for internally substepped constitutive integration.
"""
import csv
import math
from pathlib import Path

GS0, G0, H, M, REF = 110., 35., 190., 0.005, 1e-5
NAMES = [
    'voce_3pct_variable_sat_dt005_out.csv',
    'voce_3pct_variable_sat_dt0025_out.csv',
]

def load(path):
    with path.open(newline='') as f:
        reader=csv.DictReader(f)
        required={'time', 'stress_zz', 'strain_zz', 'Gamma_dot', 'gs_formula_saved', 'gs_minus_g0_saved'}
        required|={f'gss_{i:02}_num' for i in range(1,13)}
        required|={f'Lambda_plane_{p}_dot' for p in range(1,5)}
        missing=required-set(reader.fieldnames or [])
        if missing: raise ValueError(f'{path.name}: missing columns: {sorted(missing)}')
        rows=[{k:float(v) for k,v in row.items() if v not in ('',None)} for row in reader]
    if len(rows)<2: raise ValueError(f'{path}: too few rows')
    if any(not all(math.isfinite(v) for v in row.values()) for row in rows):
        raise ValueError('Nonfinite CSV value')
    if any(rows[i]['time']<=rows[i-1]['time'] for i in range(1,len(rows))):
        raise ValueError('Times are not strictly increasing')
    return rows

def gs(rate):
    if rate<0: raise ValueError('Negative total absolute slip rate')
    return GS0 if rate==0 else GS0*(rate/REF)**M

def slope(g,rate,weighted):
    if weighted < -1e-14: raise ValueError('Negative weighted absolute slip rate')
    sat=gs(max(0.,rate))
    if sat<=G0:
        raise ValueError(f'Rate-dependent saturation inadmissible: gs={sat:.8g} <= g0={G0}')
    return H*((sat-g)/(sat-G0))**2*max(weighted,0.)

def rk4_step(g, prev, curr, plane, microsteps=24):
    dt=curr['time']-prev['time']
    v0,v1=prev['Gamma_dot'],curr['Gamma_dot']
    name=f'Lambda_plane_{plane}_dot'
    w0,w1=prev[name],curr[name]
    def f(u,y):
        return slope(y, (1-u)*v0+u*v1, (1-u)*w0+u*w1)
    h=dt/microsteps
    for j in range(microsteps):
        u=j/microsteps
        k1=f(u,g)
        k2=f(u+0.5/microsteps,g+0.5*h*k1)
        k3=f(u+0.5/microsteps,g+0.5*h*k2)
        k4=f(u+1/microsteps,g+h*k3)
        g+=h*(k1+2*k2+2*k3+k4)/6.
    return g

def be_step(g, curr, dt, plane):
    sat=gs(curr['Gamma_dot'])
    if sat<=G0: raise ValueError('saturation below initial strength in BE step')
    dl=max(0.,curr[f'Lambda_plane_{plane}_dot'])*dt
    x=sat-g
    if x<0:
        return None  # closed-form root assumes x>=0
    A=H*dl/(sat-G0)**2
    return sat-2*x/(1+math.sqrt(1+4*A*x))

def analyze(path):
    rows=load(path)
    sat=[gs(x['Gamma_dot']) for x in rows]
    max_gs_csv_error=max(abs(x['gs_formula_saved']-gs(x['Gamma_dot'])) for x in rows)
    if min(sat)<=G0:
        raise ValueError(f'{path.name}: at least one saved gs<=g0')
    max_spread=0.
    rows_report=[]
    for plane in range(1,5):
        keys=[f'gss_{j:02}_num' for j in range(3*plane-2,3*plane+1)]
        rk4=rows[0][keys[0]]
        be=rk4
        err_rk4=0.;err_be=0.;max_resid=0.
        for i,row in enumerate(rows):
            values=[row[k] for k in keys]
            max_spread=max(max_spread,max(values)-min(values))
            if i==0: continue
            prev=rows[i-1]
            dt=row['time']-prev['time']
            rk4=rk4_step(rk4,prev,row,plane)
            err_rk4=max(err_rk4,abs(rk4-row[keys[0]]))
            if be is not None:
                be=be_step(be,row,dt,plane)
                if be is not None: err_be=max(err_be,abs(be-row[keys[0]]))
            dL=row[f'Lambda_plane_{plane}_dot']*dt
            ratio=(gs(row['Gamma_dot'])-row[keys[0]])/(gs(row['Gamma_dot'])-G0)
            R=(row[keys[0]]-prev[keys[0]])-H*ratio**2*dL
            max_resid=max(max_resid,abs(R))
        rows_report.append({'plane':plane,'g_MOOSE':rows[-1][keys[0]],'g_RK4':rk4,
                            'g_BE':be,'final_error_RK4':rows[-1][keys[0]]-rk4,
                            'max_error_RK4':err_rk4,'max_error_BE':err_be,'max_global_BE_residual':max_resid})
    return {'name':path.name,'rows':len(rows),'stress_final':rows[-1]['stress_zz'],
            'strain_final':rows[-1]['strain_zz'],'Gamma_final':rows[-1]['Gamma_dot'],
            'gs_min_saved':min(sat),'gs_max_saved':max(sat),'gs_final_saved':sat[-1],
            'gs_reconstructed_CSV_error':max_gs_csv_error,'coplanar_spread':max_spread,
            'planes':rows_report}

def main():
    folder=Path(__file__).resolve().parent
    results=[]
    for name in NAMES:
        path=folder/name
        if not path.exists():
            print(f'Not found: {path.name}. Run the MOOSE case first.'); continue
        try: data=analyze(path)
        except ValueError as e:
            print(f'ERROR: {e}'); continue
        results.append(data)
        print(f'\n{name} | {data["rows"]-1} steps | final strain={data["strain_final"]:.6g} | '
              f'stress={data["stress_final"]:.7f} MPa')
        print(f'gs at SAVED times: min={data["gs_min_saved"]:.5f}, '
              f'max={data["gs_max_saved"]:.5f}, final={data["gs_final_saved"]:.5f} MPa; '
              f'coplanar spread={data["coplanar_spread"]:.2e} MPa')
        print(f'max difference, Python vs gs_formula_saved: {data["gs_reconstructed_CSV_error"]:.3e} MPa')
        print('Plane    MOOSE       RK4-linear    RK4-final-error    max|RK4-error|   max|global BE residual|')
        for p in data['planes']:
            print(f'{p["plane"]:5d} {p["g_MOOSE"]:11.6f} {p["g_RK4"]:12.6f} '
                  f'{p["final_error_RK4"]:+16.8f} {p["max_error_RK4"]:16.8f} '
                  f'{p["max_global_BE_residual"]:23.8g}')
    if len(results)==2:
        a,b=results
        print('\nRefinement comparison (fine − coarse):')
        print(f'  stress_zz: {b["stress_final"]-a["stress_final"]:+.8f} MPa')
        for p1,p2 in zip(a['planes'],b['planes']):
            print(f'  plane {p1["plane"]} g: {p2["g_MOOSE"]-p1["g_MOOSE"]:+.8f} MPa')
    print('\nCaveat: RK4 uses LINEARLY INTERPOLATED SAVED slip rates; it does not know the '
          'local substep histories or constitutive Newton iterations. Small errors support '
          'consistency, not exact integration verification.')

if __name__=='__main__': main()

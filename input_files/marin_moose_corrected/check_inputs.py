#!/usr/bin/env python3
import math
from pathlib import Path
K=(275.27,80.07,303.66)
B=((K[0]+90)%360,K[1],(90-K[2])%360)
print('Kocks',K,'=> Bunge',B)
for case in ('baseline','active_5dpa'):
    text=Path(case,f'moose_{case}.i').read_text()
    assert 'euler_angle_1 = 5.27' in text and 'euler_angle_2 = 80.07' in text and 'euler_angle_3 = 146.34' in text
    assert 'xmax = 0.5' in text and 'ymax = 0.5' in text and '104374' not in text
    slip=Path(case,'slip_systems_FCC_MAT1.txt').read_text().splitlines()
    assert len(slip)==12
    for line in slip:
        p=list(map(float,line.split()))
        assert len(p)==6 and abs(sum(x*y for x,y in zip(p[:3],p[3:])))<1e-12
    assert Path(case,'Mat1/fcc.sx').exists() and Path(case,'Mat1/texture.txti').exists()
    assert Path(case,f'abaqus_{case}.inp').exists()
    print(case,'structure OK')

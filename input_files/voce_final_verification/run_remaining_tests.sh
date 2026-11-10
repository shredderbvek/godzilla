#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
APP="${1:-/home/ghostrobot96/projects/godzilla/godzilla-opt}"
if [[ ! -x "$APP" ]]; then
  echo "Cannot execute MOOSE application: $APP" >&2
  exit 2
fi
printf 'Running 0.0125 s refinement with %s\n' "$APP"
"$APP" -i voce_3pct_variable_sat_dt00125.i 2>&1 | tee voce_3pct_variable_sat_dt00125.log
printf '\nTo check zero-slip branch separately, run:\n%s -i voce_zero_slip_branch.i\n' "$APP"
python3 probe_low_rate.py
python3 check_three_dt.py

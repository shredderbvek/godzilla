#!/usr/bin/env bash
# Usage: ./run_voce_suite.sh /absolute/path/to/godzilla-opt
# To run only one case, invoke: /path/to/godzilla-opt -i voce_dtmax_0p050.i
set -euo pipefail
cd -- "$(dirname -- "${BASH_SOURCE[0]}")"
APP="${1:-${APP:-}}"
if [[ -z "$APP" ]]; then
  echo "Usage: $0 /absolute/path/to/godzilla-opt" >&2
  exit 2
fi
if [[ "$APP" != /* ]]; then
  APP="$(realpath "$APP")"
fi
if [[ ! -x "$APP" ]]; then
  echo "Cannot execute MOOSE application: $APP" >&2
  exit 2
fi
for stem in \
  voce_dtmax_0p200 voce_dtmax_0p100 voce_dtmax_0p050 voce_dtmax_0p025 \
  voce_sat_rate_m0_control voce_sat_rate_m0025 voce_sat_rate_m0050 \
  voce_sat_rate_m0050_ref1e3; do
  echo "========================================================="
  echo "Running $stem"
  if "$APP" -i "${stem}.i" > "${stem}.log" 2>&1; then
    echo "Completed: ${stem}_out.csv"
  else
    echo "FAILED $stem; inspect ${stem}.log" >&2
    tail -n 35 "${stem}.log" >&2 || true
    exit 1
  fi
done
python3 check_voce_suite.py

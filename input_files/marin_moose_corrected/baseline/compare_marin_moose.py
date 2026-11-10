#!/usr/bin/env python3
"""Compare an Abaqus Marin UMAT single-element CSV with a MOOSE Voce CSV.

Run with ordinary Python 3 (not Abaqus Python):
    python3 compare_marin_moose.py abaqus_baseline_comparison.csv moose_baseline.csv

The Abaqus CSV is produced by extract_abaqus_marin_one_element.py.
The MOOSE CSV is the [Outputs] csv from the corrected moose_baseline.i.
Requires Python 3 standard library. matplotlib is optional for PNG plots.

Comparison is of S11 (Abaqus Cauchy stress) and stress_xx (MOOSE)
as functions of engineering strain, interpolated ONLY over their common range.
It does not establish that the two constitutive integration algorithms coincide.
"""

import argparse
import bisect
import csv
import math
from pathlib import Path

ABAQUS_STRAIN = ("engineering_strain_xx", "engineering_strain", "strain_xx")
ABAQUS_STRESS = ("cauchy_stress_xx_MPa", "axial_cauchy_stress_MPa", "S11", "stress_xx")
MOOSE_STRAIN = ("strain_xx", "engineering_strain_xx")
MOOSE_STRESS = ("stress_xx", "cauchy_stress_xx_MPa")


def choose_column(headers, override, choices, filename, description):
    if override:
        if override not in headers:
            raise ValueError("{}: {} column {!r} not found. Columns: {}".format(
                filename, description, override, ", ".join(headers)))
        return override
    for col in choices:
        if col in headers:
            return col
    raise ValueError("{}: could not find {} column. Available: {}.\n"
                     "Use an explicit --*-strain or --*-stress option.".format(
                         filename, description, ", ".join(headers)))


def read_curve(filename, kind, strain_override=None, stress_override=None):
    filename = Path(filename)
    with filename.open(newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        headers = reader.fieldnames or []
        if kind == "abaqus":
            strain_choices, stress_choices = ABAQUS_STRAIN, ABAQUS_STRESS
        else:
            strain_choices, stress_choices = MOOSE_STRAIN, MOOSE_STRESS
        xcol = choose_column(headers, strain_override, strain_choices,
                             str(filename), "strain")
        ycol = choose_column(headers, stress_override, stress_choices,
                             str(filename), "stress")
        points = []
        for line_number, row in enumerate(reader, 2):
            try:
                x, y = float(row[xcol]), float(row[ycol])
            except (ValueError, TypeError, KeyError):
                continue
            if math.isfinite(x) and math.isfinite(y):
                points.append((x, y))
    if len(points) < 2:
        raise ValueError("{}: fewer than 2 valid strain-stress rows".format(filename))
    points.sort(key=lambda p: p[0])

    # Collapse duplicate/near-identical strain records (frequent at zero strain).
    # They cannot be represented uniquely by a stress-vs-strain function.
    dedup = []
    discarded = 0
    cluster = [points[0]]
    for x, y in points[1:]:
        if abs(x - cluster[-1][0]) <= 1e-12:
            cluster.append((x, y))
        else:
            dedup.append((sum(p[0] for p in cluster) / len(cluster),
                          sum(p[1] for p in cluster) / len(cluster)))
            discarded += len(cluster) - 1
            cluster = [(x, y)]
    dedup.append((sum(p[0] for p in cluster) / len(cluster),
                  sum(p[1] for p in cluster) / len(cluster)))
    discarded += len(cluster) - 1
    if len(dedup) < 2:
        raise ValueError("{}: fewer than 2 distinct strain values".format(filename))
    xs = [p[0] for p in dedup]
    ys = [p[1] for p in dedup]
    return {"x": xs, "y": ys, "xcol": xcol, "ycol": ycol,
            "n": len(dedup), "duplicates": discarded, "filename": str(filename)}


def interp(curve, x):
    xs, ys = curve["x"], curve["y"]
    tol = 1e-11 * max(1.0, abs(xs[-1]))
    if x < xs[0] - tol or x > xs[-1] + tol:
        raise ValueError("Requested strain outside measured range (no extrapolation)")
    x = min(max(x, xs[0]), xs[-1])
    k = bisect.bisect_left(xs, x)
    if k == 0:
        return ys[0]
    if k == len(xs):
        return ys[-1]
    x0, x1 = xs[k - 1], xs[k]
    y0, y1 = ys[k - 1], ys[k]
    return y0 + (x - x0) * (y1 - y0) / (x1 - x0)


def write_csv(filename, fieldnames, rows):
    with Path(filename).open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(fieldnames)
        w.writerows(rows)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("abaqus_csv", help="Abaqus export (e.g. abaqus_baseline_comparison.csv)")
    ap.add_argument("moose_csv", help="MOOSE CSV (e.g. moose_baseline.csv)")
    ap.add_argument("--out-prefix", default="marin_moose", help="Output filename prefix")
    ap.add_argument("--abaqus-strain", default=None, help="Override Abaqus engineering strain column")
    ap.add_argument("--abaqus-stress", default=None, help="Override Abaqus Cauchy stress column")
    ap.add_argument("--moose-strain", default=None, help="Override MOOSE engineering strain column")
    ap.add_argument("--moose-stress", default=None, help="Override MOOSE Cauchy stress column")
    ap.add_argument("--points", type=int, default=1001,
                    help="Points on uniform common strain grid (default: 1001)")
    ap.add_argument("--elastic-strain", type=float, default=0.0002,
                    help="End strain for initial secant estimate (default: 0.0002 = 0.02%%)")
    ap.add_argument("--no-plots", action="store_true", help="Skip PNG plots")
    args = ap.parse_args()
    if args.points < 3:
        ap.error("--points must be >= 3")

    a = read_curve(args.abaqus_csv, "abaqus", args.abaqus_strain, args.abaqus_stress)
    m = read_curve(args.moose_csv, "moose", args.moose_strain, args.moose_stress)
    low = max(a["x"][0], m["x"][0])
    high = min(a["x"][-1], m["x"][-1])
    if high - low <= 1e-14:
        raise ValueError("No overlapping engineering strain range: Abaqus [{:.8g},{:.8g}], MOOSE [{:.8g},{:.8g}]".format(
            a["x"][0], a["x"][-1], m["x"][0], m["x"][-1]))
    prefix = Path(args.out_prefix)
    prefix.parent.mkdir(parents=True, exist_ok=True)

    strains = [low + (high - low) * i / (args.points - 1) for i in range(args.points)]
    sa = [interp(a, x) for x in strains]
    sm = [interp(m, x) for x in strains]
    dif = [x - y for x, y in zip(sm, sa)]  # Always MOOSE minus Abaqus.
    rmse = math.sqrt(sum(d * d for d in dif) / len(dif))
    mae = sum(abs(d) for d in dif) / len(dif)
    kmax = max(range(len(dif)), key=lambda i: abs(dif[i]))
    scale = max(abs(y) for y in sa)
    norm_rmse = 100 * rmse / scale if scale > 1e-14 else float("nan")

    merged_path = str(prefix) + "_aligned.csv"
    write_csv(merged_path,
              ["engineering_strain", "engineering_strain_percent",
               "abaqus_S11_cauchy_MPa", "moose_stress_xx_cauchy_MPa",
               "moose_minus_abaqus_MPa"],
              zip(strains, [100 * x for x in strains], sa, sm, dif))

    lines = [
        "Marin UMAT (Abaqus) vs Kalidindi-Voce (MOOSE): axial stress comparison",
        "=" * 72,
        "Abaqus input: {}  ({} points; {} duplicates collapsed)".format(
            a["filename"], a["n"], a["duplicates"]),
        "MOOSE input:  {}  ({} points; {} duplicates collapsed)".format(
            m["filename"], m["n"], m["duplicates"]),
        "Abaqus columns: strain={!r}, stress={!r}".format(a["xcol"], a["ycol"]),
        "MOOSE columns:  strain={!r}, stress={!r}".format(m["xcol"], m["ycol"]),
        "Common strain range: {:.8g} .. {:.8g} ({:.4g}% .. {:.4g}%)".format(
            low, high, 100 * low, 100 * high),
        "Uniform comparison points: {}".format(args.points),
        "",
        "RMSE (MOOSE - Abaqus): {:.8g} MPa".format(rmse),
        "Mean abs difference:  {:.8g} MPa".format(mae),
        "Max abs difference:   {:.8g} MPa at {:.5g}% strain".format(
            abs(dif[kmax]), 100 * strains[kmax]),
        "Normalized RMSE / max |Abaqus stress|: {:.5g}%".format(norm_rmse),
        "End of common range: Abaqus {:.8g} MPa; MOOSE {:.8g} MPa; delta {:+.8g} MPa".format(
            sa[-1], sm[-1], dif[-1]),
        "",
        "Stress at common engineering strains (MPa):",
        " strain(%)     Abaqus        MOOSE       MOOSE-Abaqus",
    ]
    for x in (0.0005, 0.001, 0.002, 0.005, 0.01, 0.02, 0.03, 0.04, 0.05):
        if low - 1e-12 <= x <= high + 1e-12:
            y1, y2 = interp(a, x), interp(m, x)
            lines.append(" {:9.4f}   {:11.5f}   {:11.5f}  {:+13.6f}".format(100*x, y1, y2, y2-y1))

    if low <= 0 and high >= args.elastic_strain and args.elastic_strain > 0:
        ea = (interp(a, args.elastic_strain) - interp(a, 0.0)) / args.elastic_strain
        em = (interp(m, args.elastic_strain) - interp(m, 0.0)) / args.elastic_strain
        lines.extend([
            "", "Small-strain secant (0 to {:.4g}% strain):".format(100*args.elastic_strain),
            "  Abaqus {:.6g} MPa, MOOSE {:.6g} MPa, difference {:+.6g}%".format(
                ea, em, 100*(em-ea)/ea if abs(ea)>1e-14 else float('nan')),
            "  Note: secant only; may contain slight plasticity if the interval is too large.",
        ])
    lines.extend([
        "", "Methodology and limits:",
        "  * Both curves are interpolated in engineering STRAIN (not time). No extrapolation.",
        "  * Stresses are expected to be Cauchy S11/stress_xx in MPa, not reaction/initial area.",
        "  * RMSE uses uniform sampling in the common strain range; it is NOT a solver error norm.",
        "  * Verify orientation, slip order, stress measure, rate history and hardening law separately.",
        "  * This output compares macroscopic response only; it does not verify the internal UMAT SDVs.",
    ])

    report_path = str(prefix) + "_summary.txt"
    Path(report_path).write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))
    print("\nWrote:", merged_path, report_path)

    if not args.no_plots:
        try:
            import matplotlib
            matplotlib.use("Agg")
            import matplotlib.pyplot as plt
        except ImportError:
            print("Plots skipped: matplotlib unavailable. Install with: python3 -m pip install matplotlib")
        else:
            fig, ax = plt.subplots(figsize=(7.5, 5.0))
            ax.plot([100*x for x in a["x"]], a["y"], label="Abaqus — Marin UMAT", lw=1.8)
            ax.plot([100*x for x in m["x"]], m["y"], label="MOOSE — Kalidindi Voce", lw=1.8, ls="--")
            ax.set_xlim(100*low, 100*high)
            ax.set_xlabel("Engineering strain (%)")
            ax.set_ylabel("Cauchy stress $\\sigma_{xx}$ (MPa)")
            ax.set_title("Single-crystal tension: Abaqus vs MOOSE")
            ax.grid(True, alpha=0.25)
            ax.legend()
            fig.tight_layout()
            p = str(prefix) + "_stress_strain.png"
            fig.savefig(p, dpi=220)
            plt.close(fig)
            print("Wrote:", p)

            fig, ax = plt.subplots(figsize=(7.5, 4.2))
            ax.plot([100*x for x in strains], dif, lw=1.7)
            ax.axhline(0, linewidth=0.9, color="black")
            ax.set_xlabel("Engineering strain (%)")
            ax.set_ylabel("MOOSE - Abaqus stress (MPa)")
            ax.set_title("Axial Cauchy stress difference")
            ax.grid(True, alpha=0.25)
            fig.tight_layout()
            p = str(prefix) + "_stress_difference.png"
            fig.savefig(p, dpi=220)
            plt.close(fig)
            print("Wrote:", p)


if __name__ == "__main__":
    main()

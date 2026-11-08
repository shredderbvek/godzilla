#!/usr/bin/env python3
import argparse
import csv
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

# Optional seaborn styling
try:
    import seaborn as sns
    sns.set_theme(style="whitegrid")
except ImportError:
    plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')


def parse_args():
    parser = argparse.ArgumentParser(
        description="Plot stress-strain curves dynamically from MOOSE simulation CSV output."
    )
    parser.add_argument(
        "-i", "--input", "--csv",
        dest="csv_files",
        nargs="+",
        help="Path to one or more MOOSE output CSV files (e.g. -i input_files/test_single_element_voce_out.csv)",
    )
    parser.add_argument(
        "positional_files",
        nargs="*",
        help="Positional CSV file paths (optional alternative to -i)",
    )
    parser.add_argument(
        "-o", "--output",
        help="Custom output image path (optional; default: <input_stem>.png in same directory as CSV)",
    )
    parser.add_argument(
        "--dpi",
        type=int,
        default=300,
        help="Figure DPI resolution (default: 300)",
    )
    return parser.parse_args()


def plot_single_csv(csv_path, output_path=None, dpi=300):
    csv_path = Path(csv_path).resolve()
    if not csv_path.is_file():
        raise FileNotFoundError(f"CSV file not found: {csv_path}")

    # Set output image path with the exact same stem name as the input file
    if output_path is None:
        output_path = csv_path.with_suffix('.png')
    else:
        output_path = Path(output_path).resolve()

    # Read column header
    with open(csv_path, 'r', newline='') as f:
        reader = csv.reader(f)
        header = [h.strip() for h in next(reader)]

    data = np.loadtxt(csv_path, delimiter=',', skiprows=1)
    if data.ndim == 1:
        data = data.reshape(1, -1)

    # Detect columns dynamically
    header_lower = [h.lower() for h in header]
    strain_idx = None
    stress_idx = None
    is_direct_strain = False

    # Check for dedicated strain columns first
    for candidate in ["true_strain", "eng_strain", "strain_zz", "strain"]:
        if candidate in header_lower:
            strain_idx = header_lower.index(candidate)
            is_direct_strain = True
            break

    # Check for dedicated stress columns first
    for candidate in ["true_stress", "stress_zz", "stress", "sigma"]:
        if candidate in header_lower:
            stress_idx = header_lower.index(candidate)
            break

    # Fallback to substring matching if not found
    if strain_idx is None:
        for idx, col in enumerate(header_lower):
            if "strain" in col:
                strain_idx = idx
                is_direct_strain = True
                break
            elif "disp" in col:
                strain_idx = idx
                is_direct_strain = False
                break

    if stress_idx is None:
        for idx, col in enumerate(header_lower):
            if "stress" in col:
                stress_idx = idx
                break

    if strain_idx is None:
        strain_idx = 1 if data.shape[1] > 1 else 0
    if stress_idx is None:
        stress_idx = 2 if data.shape[1] > 2 else (1 if data.shape[1] > 1 else 0)

    strain_col_name = header[strain_idx]
    stress_col_name = header[stress_idx]

    strain_raw = data[:, strain_idx]
    stress_raw = data[:, stress_idx]

    # Handle compressive stress (take absolute value if negative)
    if np.all(stress_raw <= 1e-4) and np.min(stress_raw) < -1e-4:
        stress_val = np.abs(stress_raw)
        stress_label = rf"|{stress_col_name}| (MPa)"
    else:
        stress_val = stress_raw
        stress_label = rf"{stress_col_name} (MPa)"

    # Handle strain calculation
    if is_direct_strain:
        strain_val = np.abs(strain_raw)
        strain_label = strain_col_name.replace('_', ' ').capitalize()
        # If strain values are fractions <= 1.0, convert to % for display
        if np.max(strain_val) <= 1.5:
            strain_plot = strain_val * 100.0
            strain_axis_label = f"{strain_label} (%)"
        else:
            strain_plot = strain_val
            strain_axis_label = strain_label
    else:
        # Fallback for displacement: if single-element (ElementAverage disp_z), U_z = 2 * avg
        strain_val = np.abs(strain_raw) * 2.0
        strain_plot = strain_val * 100.0
        strain_axis_label = "Engineering Strain (%)"

    plt.figure(figsize=(8, 5), dpi=dpi)
    plt.plot(strain_plot, stress_val, linestyle='-', color='#1f77b4', lw=2.2, label=csv_path.stem)

    # Annotate yield onset if there is a distinct yield transition
    if len(stress_val) > 5 and np.max(stress_val) > np.min(stress_val) + 1.0:
        yield_threshold = stress_val[0] + 0.15 * (np.max(stress_val) - stress_val[0])
        idx_candidates = np.where(stress_val >= yield_threshold)[0]
        if len(idx_candidates) > 0:
            idx_yield = idx_candidates[0]
            ax = plt.gca()
            ax.scatter([strain_plot[idx_yield]], [stress_val[idx_yield]], color='#d62728', s=45, zorder=5)
            y_offset = 0.08 * (np.max(stress_val) - np.min(stress_val))
            ax.annotate(
                rf"Yield onset" + "\n" + rf"$\sigma \approx {stress_val[idx_yield]:.1f}$ MPa",
                xy=(strain_plot[idx_yield], stress_val[idx_yield]),
                xytext=(strain_plot[idx_yield] + 0.25, stress_val[idx_yield] + y_offset),
                arrowprops=dict(arrowstyle="->", lw=1.2, color='#d62728'),
                bbox=dict(boxstyle="round,pad=0.3", facecolor="#ffebee", edgecolor="#d62728"),
                fontsize=9,
            )

    plt.xlabel(strain_axis_label, fontsize=11)
    plt.ylabel(stress_label, fontsize=11)
    plt.title(f'Stress-Strain Response: {csv_path.stem}', fontsize=12, fontweight='bold')
    plt.legend(loc='lower right', frameon=True)
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.tight_layout()

    plt.savefig(output_path, dpi=dpi)
    plt.close()
    print(f"Saved plot to: {output_path}")
    return output_path


def main():
    args = parse_args()
    input_files = []
    if args.csv_files:
        input_files.extend(args.csv_files)
    if args.positional_files:
        input_files.extend(args.positional_files)

    # Fallback to default file if no argument provided
    if not input_files:
        script_dir = Path(__file__).resolve().parent
        candidate = script_dir.parent / "test_single_element_voce_out.csv"
        if candidate.is_file():
            input_files.append(str(candidate))
        else:
            print("Error: No CSV file provided. Use -i <path_to_csv>.")
            return

    for file_str in input_files:
        out = args.output if (len(input_files) == 1 and args.output) else None
        plot_single_csv(file_str, output_path=out, dpi=args.dpi)


if __name__ == "__main__":
    main()

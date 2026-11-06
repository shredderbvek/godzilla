#!/bin/bash

# ==============================================================================
# SLURM Configuration for Godzilla MOOSE Simulation
# Optimized for CAMML Lab Account (account: mam, partition: inv-camml)
# ==============================================================================
#SBATCH --job-name=godzilla
#SBATCH --account=mam
#SBATCH --partition=inv-camml

# Dedicated CAMML investor node hardware: 2 sockets x 20 cores = 40 cores/node
# Optimal MOOSE CP layout: 10 MPI ranks x 4 OpenMP threads = 40 CPU cores
#SBATCH --nodes=1
#SBATCH --ntasks=10
#SBATCH --cpus-per-task=4

# Exclusive access to the node ensures dedicated memory bandwidth and full ~750GB RAM
#SBATCH --exclusive

# Maximum runtime (inv-camml allows up to 7 days)
#SBATCH --time=7-00:00:00

#SBATCH --output=godzilla-slurm-%j.out
#SBATCH --error=godzilla-slurm-%j.err

set -e

# Load MOOSE environment
if [[ -f "$HOME/moose-env.sh" ]]; then
    source "$HOME/moose-env.sh"
fi

# Move to Godzilla directory
cd "${SLURM_SUBMIT_DIR:-$HOME/projects/godzilla}"

# Parse command line flags
INPUT_FILE=""
EXTRA_ARGS=()

while [[ $# -gt 0 ]]; do
    case "$1" in
        -i|--input)
            if [[ -n "${2:-}" && ! "$2" =~ ^- ]]; then
                INPUT_FILE="$2"
                shift 2
            else
                echo "Error: Argument for $1 is missing." >&2
                exit 1
            fi
            ;;
        -i=*|--input=*)
            INPUT_FILE="${1#*=}"
            shift 1
            ;;
        -h|--help)
            echo "Usage: sbatch godzilla.sbatch -i <input_file.i> [options]"
            echo ""
            echo "Arguments:"
            echo "  -i, --input <file>   Input file name (.i) to run (required)"
            echo "  -h, --help           Show this help message"
            echo "  [options]            Additional arguments passed directly to godzilla-opt"
            exit 0
            ;;
        *)
            if [[ -z "$INPUT_FILE" && ( "$1" =~ \.i$ || -f "$1" ) ]]; then
                INPUT_FILE="$1"
            else
                EXTRA_ARGS+=("$1")
            fi
            shift 1
            ;;
    esac
done

if [[ -z "$INPUT_FILE" ]]; then
    echo "Error: No input file specified." >&2
    echo "Usage: sbatch godzilla.sbatch -i <input_file.i> [options]" >&2
    exit 1
fi

if [[ ! -f "$INPUT_FILE" ]]; then
    echo "Error: Input file '$INPUT_FILE' not found in $(pwd)" >&2
    exit 1
fi

# Thread and CPU affinity settings
export OMP_NUM_THREADS="${SLURM_CPUS_PER_TASK:-1}"
export OMP_PLACES=cores
export OMP_PROC_BIND=spread

echo "============================================================"
echo " Godzilla MOOSE Simulation"
echo "============================================================"
echo "Job ID        : ${SLURM_JOB_ID:-N/A}"
echo "Partition     : ${SLURM_JOB_PARTITION:-inv-camml}"
echo "Node(s)       : ${SLURM_JOB_NODELIST:-$(hostname)}"
echo "MPI ranks     : ${SLURM_NTASKS:-1}"
echo "Threads/rank  : ${SLURM_CPUS_PER_TASK:-1}"
echo "Total CPUs    : $((${SLURM_NTASKS:-1} * ${SLURM_CPUS_PER_TASK:-1}))"
echo "Working dir   : $(pwd)"
echo "Input file    : $INPUT_FILE"
if [[ ${#EXTRA_ARGS[@]} -gt 0 ]]; then
    echo "Extra args    : ${EXTRA_ARGS[*]}"
fi
echo "Start time    : $(date)"
echo "============================================================"

# Run Godzilla with Slurm srun or fallback to mpirun outside Slurm
if [[ -n "${SLURM_JOB_ID:-}" ]]; then
    srun --cpu-bind=cores ./godzilla-opt \
        -i "$INPUT_FILE" \
        --n-threads="${SLURM_CPUS_PER_TASK:-1}" \
        "${EXTRA_ARGS[@]}"
else
    mpirun -n "${SLURM_NTASKS:-1}" ./godzilla-opt \
        -i "$INPUT_FILE" \
        --n-threads="${SLURM_CPUS_PER_TASK:-1}" \
        "${EXTRA_ARGS[@]}"
fi

echo
echo "============================================================"
echo "Simulation completed"
echo "End time      : $(date)"
echo "============================================================"

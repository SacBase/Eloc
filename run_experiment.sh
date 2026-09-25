#!/bin/bash

#SBATCH --account=csmpi
#SBATCH --partition=csmpi_fpga_long
#SBATCH --cpus-per-task=16
#SBATCH --mem=16G
#SBATCH --gres=gpu:0
#SBATCH --time=1:00:00
#SBATCH --output=results/slurm/eloc-%j.out
#SBATCH --error=results/slurm/eloc-%j.err

RUN_NR=$SLURM_ARRAY_TASK_ID

# Capture arguments required to run eloc
EXEC=()
NR_EXEC=$1
i=0
shift

while [ $i -lt $NR_EXEC ]; do
  ((i++))
  EXEC+=" $1"
  shift
done

# Capture remaining arguments
META_ARGS="$@"

# Get eloc environment variables (Lx, Ly, alpha, ...)
EXEC_ARGS=`awk "NR==$RUN_NR" tmp/runs.txt`

# Run eloc
echo $EXEC $EXEC_ARGS $META_ARGS
$EXEC $EXEC_ARGS $META_ARGS
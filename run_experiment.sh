#!/bin/bash

#SBATCH --account=csmpi
#SBATCH --partition=csmpi_fpga_long
#SBATCH --cpus-per-task=1
#SBATCH --mem=1G
#SBATCH --gres=gpu:0
#SBATCH --time=1:00:00
#SBATCH --output=results/slurm/eloc-%j.out
#SBATCH --error=results/slurm/eloc-%j.err

RUN_NR=$SLURM_ARRAY_TASK_ID
EXEC="$@"

EXEC_ARGS=`awk "NR==$RUN_NR" tmp/runs.txt`

$EXEC $EXEC_ARGS
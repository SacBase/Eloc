#!/bin/bash

PYTHON_EXEC="python3"

# Experiment variables:
ALPHA=2
GAMMA=0.5
RUNS=1000
SEED=0

# Lx and Ly's
EXP=()
NR_POS_ARGS=0
is_number="^[0-9]+$"

# Languages
SAC=0
SAC_MT=()
MT_COUNT=0
PYTHON=0

while [[ $# -gt 0 ]]; do
  case $1 in
    -a=*)
      tmp=$1
      ALPHA=${tmp:3}
      shift # past argument
      ;;
    -g=*)
      tmp=$1
      GAMMA=${tmp:3}
      shift # past argument
      ;;
    -seed=*)
      tmp=$1
      SEED=${tmp:6}
      shift # past argument
      ;;
    -n=*)
      tmp=$1
      RUNS=${tmp:3}
      shift # past argument
      ;;
    -s)
      SAC=1
      shift
      ;;
    -smt=*)
      tmp=$1
      SAC_MT[MT_COUNT]=${tmp:5}
      ((MT_COUNT++))
      shift
      ;;
    -p)
      PYTHON=1
      shift
      ;;
    *)
      if ! [[ $1 =~ $is_number ]]; then
        echo Skipping unknown argument: $1
      else
        EXP+=($1)
        ((NR_POS_ARGS++))
      fi
      shift
      ;;
  esac
done

if [[ $(($NR_POS_ARGS % 2)) -eq 1 ]]; then
  echo setup.sh should get an even number of positional arguments 
  exit -1
fi

rm -rd tmp
mkdir tmp
touch tmp/runs.txt
i=0
NR_EXPERIMENTS=$(($NR_POS_ARGS / 2))

while [ $i -lt $NR_EXPERIMENTS ]; do
  echo ${EXP[($i*2)]} ${EXP[(($i*2)+1)]} $ALPHA $GAMMA $RUNS $SEED >> tmp/runs.txt
  ((i++))
done


# generate state and RBM:
i=1
while [ $i -le $NR_EXPERIMENTS ]; do
  echo "Generating state and RBM for experiment $i/$NR_EXPERIMENTS"
  args=`awk "NR==$i" tmp/runs.txt`
  $PYTHON_EXEC auxiliary/generate_states.py $args
  $PYTHON_EXEC auxiliary/generate_RBM.py $args
  ((i++))
done


if [ $PYTHON -eq 1 ]; then
  echo "Creating Python array job"
  P_SBATCH="--array=1-$NR_EXPERIMENTS run_experiment.sh 2 $PYTHON_EXEC eloc.py"
  sbatch $P_SBATCH
fi

if [ $SAC -eq 1 ]; then
  echo "Compiling sequential eloc.sac"
  sac2c eloc.sac -o tmp/sac_seq.out
  echo "Creating sac sequential array job"
  S_SBATCH="--array=1-$NR_EXPERIMENTS run_experiment.sh 1 ./tmp/sac_seq.out"
  sbatch $S_SBATCH
fi

if [ ${#SAC_MT[@]} -gt 0 ]; then
  echo "Compiling multi-threaded eloc.sac"
  sac2c -tmt_pth eloc.sac -o tmp/sac_mt.out
  for tc in ${SAC_MT[@]}; do
    echo "Creating $tc-threadded sac array job"
    SMT_SBATCH="--array=1-$NR_EXPERIMENTS run_experiment.sh 1 ./tmp/sac_mt.out -mt $tc -id $tc"
    sbatch $SMT_SBATCH
  done
fi
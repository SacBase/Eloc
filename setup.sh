#!/bin/bash

PYTHON_EXEC="python3"
SAC_EXEC="./a.out"

# Experiment variables:
ALPHA=2
GAMMA=0.5
RUNS=1000
SEED=0

# Lx and Ly's
EXP=()
NR_POS_ARGS=0
is_number="^[0-9]+$"

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
    -s=*)
            tmp=$1
      SEED=${tmp:3}
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
  echo setup.sh should get an even number of positional integer arguments 
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
        echo $i
        args=`awk "NR==$i" tmp/runs.txt`
        $PYTHON_EXEC auxiliary/generate_states.py $args
        $PYTHON_EXEC auxiliary/generate_RBM.py $args
        ((i++))
done


if [ $PYTHON ]; then
        P_SBATCH="--array=1-$NR_EXPERIMENTS run_experiment.sh $PYTHON_EXEC eloc.py"
        echo $P_SBATCH
        sbatch $P_SBATCH
fi

if [ $SAC ]; then
        S_SBATCH="--array=1-$NR_EXPERIMENTS run_experiment.sh $SAC_EXEC"
        echo $S_SBATCH
        sbatch $S_SBATCH
fi
#!/bin/bash
#SBATCH -N 1
#SBATCH --mem=16384
#SBATCH -n 1
#SBATCH --time=0
#SBATCH -p gpu
#SBATCH --gres=gpu:1

module load anaconda3
source activate CONDA_ENVIRONMENT
python -u search_gpu.py

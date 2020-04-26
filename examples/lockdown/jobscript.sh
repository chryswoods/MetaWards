#!/bin/bash
#PBS -l walltime=01:00:00
#PBS -l select=4:ncpus=64:mem=64GB
# The above sets 4 nodes with 64 cores each

# source the version of metawards we want to use
# (assumes your python environments are in $HOME/envs)
source $HOME/envs/metawards-0.9.0/bin/activate

# change into the directory from which this job was submitted
cd $PBS_O_WORKDIR

# if you need to change the path to the MetaWardsData repository,
# then update the below line and uncomment
#export METAWARDSDATA="$HOME/GitHub/MetaWardsData"

metawards -u lockdown.inp --iterator lockdown.py \
          -a ExtraSeedsLondon.dat -i scan.csv --nsteps 150 \
          --repeats 8 --nthreads 16 --force-overwrite-output

#!/usr/bin/env bash

#SBATCH --job-name=pv-experiment
#SBATCH --output=pv-experiment.log
#SBATCH --account tyche
#SBATCH --time=240:00:00
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1


export TZ=:/etc/localtime


proot -b $HOME/nix:/nix bash << EOT
. $HOME/.nix-profile/etc/profile.d/nix.sh

TIME="`which time` --verbose"

date -u

$TIME ./pv-experiment.py

date -u

EOT

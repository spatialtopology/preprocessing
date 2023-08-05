#!/bin/bash -l
#SBATCH --job-name=fmriprepgr
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=12
#SBATCH --mem-per-cpu=40G
#SBATCH --time=01:00:00
#SBATCH -o ./logcorr/fmriprepgr_%A_%a.o
#SBATCH -e ./logcorr/fmriprepgr_%A_%a.e
#SBATCH --account=DBIC
#SBATCH --partition=standard

mkdir -p ./logcorr

conda init bash

conda activate biopac
# conda activate spacetop_env

#/dartfs-hpc/rc/lab/C/CANlab/labdata/data/WASABI/scripts/fmriprep/fmriprep-group-report/fmriprepgr/reports.py \

# /dartfs-hpc/rc/lab/C/CANlab/labdata/data/spacetop_data/scripts_qc/fmriprep-group-report/fmriprepgr 
# /dartfs-hpc/rc/lab/C/CANlab/labdata/data/WASABI/scripts/fmriprep/fmriprep-group-report/fmriprepgr

fmriprepgr \
--reports_per_page 50 \
--drop_background dseg \
--drop_background pepolar \
/dartfs-hpc/rc/lab/C/CANlab/labdata/data/WASABI/derivatives/fmriprep/

# @click.option('--reports_per_page', default=50,
#               help='How many figures per page. If None, then put them all on a single page.')
# @click.option('--flip_images', '-f', default=(), multiple=True,
#               help="The names of any report subsections where you want to flip which image is shown when mousing over."
#                    " Can be passed multiple times to specify multiple subsections.")
# @click.option('--drop_background', default=(), multiple=True,
#               help="The names of any report subsections where you want to drop the image that shows before mousing over"
#                    " and just see the image that's shown when mousing over. Can be passed multiple times to specify"
#                    " multiple subsections.")
# @click.option('--drop_foreground', default=(), multiple=True,
#               help="The names of any report subsections where you want to drop the image that shows after mousing over"
#                    " and just see the image that's shown before mousing over. Can be passed multiple times to specify"
#                    " multiple subsections.")
# @click.argument('fmriprep_output_path')
#!/usr/bin/env python3
# Author: Stephen Mather with approach borrowed from Piero Toffanin
# License: AGPLv3

import os
import sys
sys.path.insert(0, os.path.join("..", "..", os.path.dirname(__file__)))

import argparse
import multiprocessing
from opendm.dem.merge import euclidean_merge_dems
from opendm.dem import utils

parser = argparse.ArgumentParser(description='Generate merged DEMs using ODM\'s algorithm.')
parser.add_argument('dem_paths',
                type=str,
                help='Path to dem files (*.tif)')
parser.add_argument('--type',
                    type=str,
                    choices=("dsm", "dtm"),
                    default="dsm",
                    help="Type of DEM. Default: %(default)s")
parser.add_argument('--resolution',
                type=float,
                default=0.05,
                help='Resolution in m/px. Default: %(default)s')
parser.add_argument('--gapfill-steps',
                    default=3,
                    type=int,
                    help='Number of steps used to fill areas with gaps. Set to 0 to disable gap filling. '
                            'Starting with a radius equal to the output resolution, N different DEMs are generated with '
                            'progressively bigger radius using the inverse distance weighted (IDW) algorithm '
                            'and merged together. Remaining gaps are then merged using nearest neighbor interpolation. '
                            'Default: %(default)s')
args = parser.parse_args()

if not os.path.exists(args.dem_paths):
    print("%s does not exist" % args.dem_paths)
    exit(1)

outdir = os.path.dirname(args.dems_path)


def get_dem_paths(dem_paths):
    """
    :return Existing paths for all dems
    """

    if not os.path.exists(dem_paths):
            return result

    result=os.listdir(dem_paths)

    return result

commands.euclidean_merge_dems(os.listdir(dem_paths), os.path.join(outdir, 'merged_dem', get_dem_vars(), euclidean_map_source=None)



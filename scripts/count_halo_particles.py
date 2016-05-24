#!/usr/bin/env python
# counthaloparticles.py
# Count halo particles for a given enzo directory.
# Define custom quantity functions here.
# counthaloparticles.py RD0006

import argparse
parser = argparse.ArgumentParser()
parser.add_argument("directory", type=str, help="List one or more directories to analyze.")
args = parser.parse_args()
directory = args.directory

import yt
from yt.analysis_modules.halo_analysis.api import HaloCatalog
from yt.analysis_modules.halo_analysis.halo_callbacks import add_callback

ds = yt.load(directory+'/'+directory)
halos_ds = yt.load('halo_catalogs/catalog/catalog.0.h5')
hc = HaloCatalog(data_ds=ds, halos_ds=halos_ds)
hc.load()

def count_particles(halo):
    """
    Creates a 30kpc sphere around a center of mass and counts the number of contained particles.
    """
    x = halo.quantities['particle_position_x']
    y = halo.quantities['particle_position_y']
    z = halo.quantities['particle_position_z']

    sphere = halo.halo_catalog.data_ds.sphere([x, y, z], (30, 'kpc'))
    n_particles = len(sphere['x'])

    halo.particle_count = n_particles
    print halo.particle_count

add_callback('count_particles', count_particles)

# Run the analysis.
hc.add_callback('count_particles')
hc.create()
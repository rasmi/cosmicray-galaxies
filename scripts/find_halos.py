#!/usr/bin/env python
# findhalos.py
# Find halos for a given enzo directory.
# findhalos.py RD0006

import argparse
parser = argparse.ArgumentParser()
parser.add_argument("directory", type=str, help="List one or more directories to analyze.")
args = parser.parse_args()
directory = args.directory

import yt
from yt.analysis_modules.halo_analysis.api import HaloCatalog
from yt.analysis_modules.halo_analysis.halo_filters import add_filter

ds = yt.load(directory+'/'+directory)
hc = HaloCatalog(data_ds=ds, finder_method='hop')

# Define custom filters.
def filter_position(halo):
    """
    Checks to see if the particle position is within the defined boundaries.
    """
    lower_bound = 0.375
    upper_bound = 0.625
    x = halo.quantities['particle_position_x']
    y = halo.quantities['particle_position_y']
    z = halo.quantities['particle_position_z']

    return (lower_bound < x < upper_bound) and (lower_bound < y < upper_bound) and (lower_bound < z < upper_bound)

def filter_particles(halo):
    """
    Checks to see if there are more than a certain number of particles within a sphere.
    """
    minimum_particles = 50000
    x = halo.quantities['particle_position_x']
    y = halo.quantities['particle_position_y']
    z = halo.quantities['particle_position_z']

    sphere = halo.halo_catalog.data_ds.sphere([x, y, z], (30, 'kpc'))
    n_particles = len(sphere['x'])

    return n_particles > minimum_particles

# Add to the filter registry.
add_filter('position', filter_position)
add_filter('particles', filter_particles)

# Run the analysis.
hc.add_filter('quantity_value', 'particle_mass', '<', 1e13, 'Msun')
hc.add_callback('iterative_center_of_mass')
hc.add_filter('position')
hc.add_filter('particles')

hc.create()
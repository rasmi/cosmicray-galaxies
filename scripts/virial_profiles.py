#!/usr/bin/env python
# virial_profiles.py
# Create halo projections for gas, stars, and dm density for a given enzo directory.
# virial_profiles.py RD0006

import argparse
parser = argparse.ArgumentParser()
parser.add_argument("directory", type=str, help="List one or more directories to analyze.")
args = parser.parse_args()
directory = args.directory

import numpy as np
import yt
from yt.analysis_modules.halo_analysis.api import HaloCatalog


fields = {
    'gas': ('gas', 'density'),
    'stars': ('deposit', 'stars_density'),
    'dark_matter': ('deposit', 'dark_matter_density')
}


def stars(pfilter, data):
    filter = data[(pfilter.filtered_type, 'particle_type')] == 2
    return filter

def dark_matter(pfilter, data):
    filter = data[(pfilter.filtered_type, 'particle_type')] == 1
    return filter

yt.add_particle_filter('stars', function=stars, filtered_type='all', requires=['particle_type'])
yt.add_particle_filter('dark_matter', function=dark_matter, filtered_type='all', requires=['particle_type'])

ds = yt.load(directory+'/'+directory)
ds.add_particle_filter('stars')
ds.add_particle_filter('dark_matter')

halos_ds = yt.load('halo_catalogs/catalog/catalog.0.h5')
hc = HaloCatalog(data_ds=ds, halos_ds=halos_ds)
hc.add_callback("sphere", factor=2.0)
hc.add_callback("profile", ["radius"], [("gas", "overdensity")], weight_field="cell_volume", accumulation=True, storage="virial_quantities_profiles")
hc.add_callback("virial_quantities", ["radius"], profile_storage = "virial_quantities_profiles")
hc.add_callback('sphere', radius_field='radius_200', factor=5, field_parameters=dict(virial_radius=('quantity', 'radius_200')))

hc.add_callback('profile', 'virial_radius_fraction', [('gas','temperature')], storage='virial_profiles', weight_field='cell_mass', accumulation=False, output_dir='profiles')
hc.load()

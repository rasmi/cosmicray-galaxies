#!/usr/bin/env python
# halo_profiles.py
# Create halo profiles for gas, stars, and dm density for a given enzo directory.
# halo_profiles.py RD0006

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
hc.load()
halos = hc.halo_list

for index, halo in enumerate(halos):
    com = [halo.quantities['particle_position_x'], halo.quantities['particle_position_y'], halo.quantities['particle_position_z']]
    sp = ds.sphere(com, (20, 'kpc'))
    profiles = []
    labels = []
    for fieldname, field in fields.iteritems(): 
        profiles.append(yt.create_profile(sp, 'radius', field))
        labels.append(fieldname)
    plot = yt.ProfilePlot.from_profiles(profiles, labels=labels)
    plot.set_unit('radius', 'kpc')
    plot.save('%s_%d_profile.png' % (ds, index))
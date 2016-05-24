#!/usr/bin/env python
# halo_projections.py
# Create halo projections for gas, stars, and dm density for a given enzo directory.
# halo_projections.py RD0006

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

for fieldname, fieldvalue in fields.iteritems():
    for index, halo in enumerate(halos):
        com = [halo.quantities['particle_position_x'], halo.quantities['particle_position_y'], halo.quantities['particle_position_z']]
        sp = ds.sphere(com, (30, 'kpc'))
        amv = sp.quantities.angular_momentum_vector()
        center = sp.quantities.center_of_mass()
        res = 1024
        width = [0.01, 0.01, 0.01]
        image = yt.off_axis_projection(ds, center, amv, width, res, fieldvalue)
        yt.write_image(np.log10(image), '%s_%d_%s_offaxis_projection.png' % (ds, index, fieldname))
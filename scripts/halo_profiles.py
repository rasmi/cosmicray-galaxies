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
import matplotlib
matplotlib.use('Agg')
import yt
from yt.analysis_modules.halo_analysis.api import HaloCatalog
import matplotlib.pyplot as plt

fields = {
    'gas': ('gas', 'density'),
    'stars': ('deposit', 'stars_density'),
    'dark_matter': ('deposit', 'dark_matter_density'),
    'radius': ('index', 'virial_radius_fraction')
}

units = {field: 'Msun/kpc**3' for field in fields.values()}
units.update({'radius': 'kpc'})

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
hc.add_callback('load_profiles', storage='virial_profiles', output_dir='profiles')
hc.load()
halos = hc.halo_list

def profile_plot(halo, filename):
    #print halo
    radius = halo.virial_profiles[u"('index', 'virial_radius_fraction')"]
    temperature = halo.virial_profiles[u"('gas', 'temperature')"]
    com = [halo.quantities['particle_position_x'], halo.quantities['particle_position_y'], halo.quantities['particle_position_z']]
    #print com
    sp = ds.sphere(com, (30, 'kpc'))
    profiles = yt.create_profile(sp, 'radius', fields.values(), units=units)
    #for fieldname, field in fields.iteritems():
    plt.loglog(np.array(radius), np.array(temperature))
    #plt.xlim([profiles.x.min(), profiles.x.max()])
    plt.xlabel('Radius $[kpc]$')
    #plt.ylabel('$\\rho [M_{\odot} kpc^{-3}]$')
    plt.legend(loc='best')
    plt.savefig(filename)
    plt.clf()

for index, halo in enumerate(halos):
    profile_plot(halo, '%s_%d_profile.png' % (ds, index))
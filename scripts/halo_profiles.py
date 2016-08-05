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
import matplotlib.pyplot as plt

fields = {
    'gas': ('gas', 'density'),
    'stars': ('deposit', 'stars_density'),
    'dark_matter': ('deposit', 'dark_matter_density')
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

halo_centers = np.genfromtxt('centers.csv', delimiter=',')
halos = []
for center in halo_centers:
    halos.append(ds.arr(center, 'code_length'))

def profile_plot(center_of_mass, filename):
    sp = ds.sphere(center_of_mass, (30, 'kpc'))
    profiles = yt.create_profile(sp, 'radius', fields.values())
    for fieldname, field in fields.iteritems():
        plt.loglog(profiles.x, profiles[field], label=fieldname)
    plt.xlim([profiles.x.min(), profiles.x.max()])
    plt.xlabel('Radius $[kpc]$')
    plt.ylabel('$\\rho [M_{\odot} kpc^{-3}]$')
    plt.legend(loc='best')
    plt.savefig(filename)
    plt.clf()

for index, center_of_mass in enumerate(halos):
    profile_plot(center_of_mass, '%s_%d_profile.png' % (ds, index))
import numpy as np
import matplotlib
matplotlib.use('Agg')
import yt
from yt.analysis_modules.halo_analysis.api import HaloCatalog
import matplotlib.pyplot as plt

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

directory = 'RD0009'

ds = yt.load(directory+'/'+directory)
ds.add_particle_filter('stars')
ds.add_particle_filter('dark_matter')

halos_ds = yt.load('halo_catalogs/catalog/catalog.0.h5')
hc = HaloCatalog(data_ds=ds, halos_ds=halos_ds)
hc.load()
halos = hc.halo_list

fieldname = 'gas'
fieldvalue = fields[fieldname]
index = 1
halo = halos[index]

# PROJECTION PLOT
com = [halo.quantities['particle_position_x'], halo.quantities['particle_position_y'], halo.quantities['particle_position_z']]
sp = ds.sphere(com, (30, 'kpc'))
amv = sp.quantities.angular_momentum_vector()
amv = amv / np.sqrt((amv**2).sum())
center = sp.quantities.center_of_mass()
res = 1024
width = [0.01, 0.01, 0.01]
image = yt.off_axis_projection(ds, center, amv, width, res, fieldvalue)
yt.write_image(np.log10(image), '%s_%d_%s_offaxis_projection.png' % (ds, index, fieldname))

# PROFILE PLOT
com = [halo.quantities['particle_position_x'], halo.quantities['particle_position_y'], halo.quantities['particle_position_z']]
sp = ds.sphere(com, (30, 'kpc'))
profiles = yt.create_profile(sp, 'radius', fields.values())
for fieldname, field in fields.iteritems():
    plt.loglog(profiles.x, profiles[field], label=fieldname)
plt.xlim([profiles.x.min(), profiles.x.max()])
plt.xlabel('Radius $[kpc]$')
plt.ylabel('$\\rho [M_{\odot} kpc^{-3}]$')
plt.legend(loc='best')
plt.savefig('%s_%d_profile.png' % (ds, index))
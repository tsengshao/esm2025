import numpy as np
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import sys, os
sys.path.insert(0, '../')
import utils.utils_plot_cartopy as ucrs
import utils.era5  as uera5
import utils.imerg as uimerg
import utils.taiesm  as utaiesm
from datetime import datetime, timedelta
from netCDF4 import Dataset
import multiprocessing

reg_str = 'NWPac'
reg_str = 'tropics'
#stime = datetime(2016,8,1)
#stime = datetime(2016,8,5)
ptools  = ucrs.PlotTools_cartopy()
lonb, latb, _, _ = ptools.get_region_boundary_and_interval(reg_str)

#nt = int((datetime(2016,8,15)-stime).total_seconds()/3600)
nt = 241
tunits = 'hourly'

# read taiesm dataset
fdir  = '/data/C.shaoyu/TaiESM/archive/'
exp   = 'f02.F2000.hindcast'
exp   = 'f02.F2000.hindcast_SSTp3k'
reg   = lonb+latb+[850, 850]
esm   =  utaiesm.TaiESMRetriever(fdir, exp, reg, iens=4)
print(exp)

#np.savez(f'{exp}_den', den=den)
den = np.load(f'{exp}_den.npz')['den']

plt.close('all')
fig, proj, ax, cax0, cax1 = ptools.create_fig(reg_str)
cax1.set_axis_off()

#bounds, norm, cmap = ptools.get_cmap_of_pcp(bounds=[0.1, 0.5, 1, 2, 5])
bounds, norm, cmap = ptools.get_cmap_of_pcp(bounds=[0, 5, 10, 15, 25])
bounds, norm, cmap = ptools.get_cmap_of_pcp(bounds=[0, 5, 10, 25, 50])
data = np.where(den>bounds[0], den, np.nan)
PC = ax.pcolormesh(esm.LON, esm.LAT, data, 
                   norm=norm, cmap=cmap, transform=proj,alpha=0.7)
plt.colorbar(PC, cax0)

#CO = ax.contour(esm.LON,esm.LAT, tc_mask, levels=[0.5], transform=proj, linewidths=[3], colors=['g'])

plt.sca(ax)
#datestr = nowtime.strftime('%Y%m%d_%H')
plt.title(f'TaiESM_f02', loc='left', fontweight='bold', fontsize=15)
plt.title(f'{exp}\nTC number', loc='right', fontsize=13)

plt.savefig(f'./fig/vort_taiesm/{exp}_tcnum.png', facecolor='w', bbox_inches='tight', dpi=250)






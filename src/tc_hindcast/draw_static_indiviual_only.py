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


#for exp in ['f02.F2000.hindcast', 'f02.F2000.hindcast_SSTp3k']:
explist = ['f02.F2000.hindcast', 'f02.F2000.hindcast_SSTp3k']
explist_short = ['control', 'SSTp3k']

varname_dict={'ws':'Max_WindSpeed@850hPa',\
              'rain':'Max_Rain',
             }
varunits_dict={'ws':'m/s',\
              'rain':'mm/hr',
             }
var='ws'
for var in ['ws', 'rain']:
    fig, ax = plt.subplots()
    for iexp in range(2):
        exp = explist[iexp]
        c = np.load(f'{exp}_indiviual.npz')
        data = c[var]
        pr = np.percentile(data, [10, 25, 50, 75, 90])
        mean = data.mean()
        x = iexp+1
        width = 0.4
        plt.plot([x,x],pr[[0,4]], 'k', lw=2)
        ax.add_patch(plt.Rectangle((x-width/2,pr[1]), width, pr[3]-pr[1], ls="-", lw=2, ec="k", fc="white"))
        plt.plot([x-width/2, x+width/2], [pr[2], pr[2]], 'k', lw=2,zorder=10)
        plt.scatter(x, mean, s=100, fc='r',zorder=20)
    plt.xticks([1,2], explist_short)
    plt.xlim(0, 3)
    plt.ylabel(f'[{varunits_dict[var]}]')
    plt.title(varname_dict[var], loc='left', fontsize=20, fontweight='bold')
    plt.savefig(f'box_{var}.png', dpi=250, bbox_inches='tight')
    plt.close('all')


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

reg_str = 'NWPac'
stime = datetime(2016,8,1)
ptools  = ucrs.PlotTools_cartopy()
lonb, latb, _, _ = ptools.get_region_boundary_and_interval(reg_str)

nt = int((datetime(2016,8,11)-stime).total_seconds()/3600)
tunits = 'hourly'

# read taiesm dataset
fdir  = '/data/C.shaoyu/TaiESM/archive/'
exp   = 'f02.F2000.hindcast'
reg   = lonb+latb+[850, 850]
esm   =  utaiesm.TaiESMRetriever(fdir, exp, reg, iens=0)

## 
for it in range(nt):
    nowtime = stime+timedelta(hours=it)
    print(it, nowtime)
    tseries_esm,  data_u = esm.get_data(nt=1, var='U850', mean=None, stime=nowtime)
    tseries_esm,  data_v = esm.get_data(nt=1, var='V850', mean=None, stime=nowtime)
    tseries_esm,  data_pr = esm.get_data(nt=1, var='PRECT', mean=None, stime=nowtime)
    data_pr *= 3600.

    # read data
    dx = (esm.LON[1] - esm.LON[0])*111000.
    dy = (esm.LAT[1] - esm.LAT[0])*111000.
    weight = np.cos(esm.LAT[:,np.newaxis]*np.pi/180.)
    data_vort = np.gradient(data_v,axis=1)/dx - np.gradient(data_u,axis=0)/dy
    data_vort *= weight
    
    plt.close('all')
    fig, proj, ax, cax0, cax1 = ptools.create_fig(reg_str)
    levels=[3.5, 7.9, 12.3, 16.7, 21.1, 25.5]
    CO = ax.contourf(esm.LON,esm.LAT, data_vort*1e5, levels=levels, cmap=plt.cm.YlOrBr, extend='max', transform=proj)
    plt.colorbar(CO, cax0)
    
    skip = (slice(None, None, 5), slice(None, None, 5))
    data_mask = np.where((data_u**2+data_v**2)**0.5>=15, True, False)
    datau = np.where(data_mask, data_u, np.nan)
    QV = ax.quiver(esm.LON[skip[1]], esm.LAT[skip[0]], 
               datau[skip], data_v[skip],
               angles='xy', scale_units='xy', scale=15,
               width=0.002, headwidth=3,
               color='b', transform=proj,
              )
    
    bounds, norm, cmap = ptools.get_cmap_of_pcp(bounds=[0.1, 0.5, 1, 2, 5])
    data = np.where(data_pr>=bounds[0], data_pr, np.nan)
    PC = ax.pcolormesh(esm.LON, esm.LAT, data, 
                       norm=norm, cmap=cmap, transform=proj,alpha=0.7)
    plt.colorbar(PC, cax1)
    
    plt.sca(ax)
    datestr = nowtime.strftime('%Y%m%d_%H')
    plt.title(f'{datestr}\nTaiESM_f02', loc='left', fontweight='bold', fontsize=15)
    plt.title(f'{esm.EXP}\nvort850[1e-5], preci.[mm/hr]', loc='right', fontsize=13)
    
    os.system(f'! mkdir -p ./fig/vort_taiesm/{esm.EXP}')
    plt.savefig(f'./fig/vort_taiesm/{esm.EXP}/vort_{datestr}.png', facecolor='w', bbox_inches='tight', dpi=250)






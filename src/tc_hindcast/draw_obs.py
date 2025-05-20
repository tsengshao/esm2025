import numpy as np
import matplotlib.pyplot as plt
import numpy as np
import sys, os
sys.path.insert(0, '../')
import utils.utils_plot_cartopy as ucrs
import utils.era5  as uera5
import utils.imerg as uimerg
from datetime import datetime, timedelta
import matplotlib.pyplot as plt


reg_str = 'NWPac'
stime = datetime(2016,8,1)
ptools  = ucrs.PlotTools_cartopy()
lonb, latb, _, _ = ptools.get_region_boundary_and_interval(reg_str)

nt = int((datetime(2016,8,11)-stime).total_seconds()/3600)
tunits = 'hourly'

# read era5 dataset 
fdir  = '/data/C.shaoyu/data/era5/cwbgfs_hourly/'
reg   = lonb+latb+[850, 850]
era5 = uera5.Era5Retriever(fdir, stime, reg)

fdir  = '/data/C.shaoyu/ESM2025/data/imerg/all_rename'
reg   = lonb+latb
imerg = uimerg.ImergRetriever(fdir, stime, reg)

## 
for it in range(nt):
    nowtime = stime+timedelta(hours=it)
    print(it, nowtime)

    # read data
    tseries_era5,  data_u = era5.get_data(nt=1, var='u', mean=None, stime=nowtime)
    tseries_era5,  data_v = era5.get_data(nt=1, var='v', mean=None, stime=nowtime)
    tseries_imerg, data_pr = imerg.get_data(nt=1, stime=nowtime, mean=tunits)
    
    dx = (era5.LON[1] - era5.LON[0])*111000.
    dy = (era5.LAT[1] - era5.LAT[0])*111000.
    weight = np.cos(era5.LAT[:,np.newaxis]*np.pi/180.)
    data_vort = np.gradient(data_v,axis=1)/dx - np.gradient(data_u,axis=0)/dy
    data_vort *= weight
    
    
    plt.close('all')
    fig, proj, ax, cax0, cax1 = ptools.create_fig(reg_str)
    levels=[3.5, 7.9, 12.3, 16.7, 21.1, 25.5]
    CO = ax.contourf(era5.LON, era5.LAT, data_vort*1e5, levels=levels, cmap=plt.cm.YlOrBr, extend='max', transform=proj)
    plt.colorbar(CO, cax0)
    
    skip = (slice(None, None, 5), slice(None, None, 5))
    data_mask = np.where((data_u**2+data_v**2)**0.5>=15, True, False)
    datau = np.where(data_mask, data_u, np.nan)
    QV = ax.quiver(era5.LON[skip[1]], era5.LAT[skip[0]], 
               datau[skip], data_v[skip],
               angles='xy', scale_units='xy', scale=15,
               width=0.002, headwidth=3,
               color='b', transform=proj,
              )
    
    bounds, norm, cmap = ptools.get_cmap_of_pcp()
    data = np.where(data_pr>=bounds[0], data_pr, np.nan)
    PC = ax.pcolormesh(imerg.LON, imerg.LAT, data, 
                       norm=norm, cmap=cmap, transform=proj,alpha=0.7)
    plt.colorbar(PC, cax1)
    
    plt.sca(ax)
    datestr = nowtime.strftime('%Y%m%d_%H')
    plt.title(f'{datestr}\nERA5/IMERG', loc='left', fontweight='bold', fontsize=15)
    plt.title(f'vort850[1e-5], preci.[mm/hr]', loc='right', fontsize=13)
    
    os.system('! mkdir -p ./fig/vort_obs')
    plt.savefig(f'./fig/vort_obs/vort_{datestr}.png', facecolor='w', bbox_inches='tight', dpi=250)






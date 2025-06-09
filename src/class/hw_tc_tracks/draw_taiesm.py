import numpy as np
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import sys, os
sys.path.insert(0, '../')
import utils.utils_plot_cartopy as ucrs
import utils.taiesm  as utaiesm
from datetime import datetime, timedelta
from netCDF4 import Dataset

reg_str = 'NWPac'
stime = datetime(2016,8,1)
ptools  = ucrs.PlotTools_cartopy()
lonb, latb, _, _ = ptools.get_region_boundary_and_interval(reg_str)

nt = int((datetime(2016,8,11)-stime).total_seconds()/3600)
nt = 14*24+1 
stime = datetime(2017,9,11)

tunits = 'hourly'

# read taiesm dataset
fdir  = '/data/C.shaoyu/TaiESM/archive/'
exp   = 'f02.F2000.hindcast'
exp   = 'f02.F2000.hindcast_SSTp3k'
#/work1/eddie7824/ESM/f09.F2000.ESM_Hindcast_20170907
fdir  = '/work1/eddie7824/ESM/'
exp   = 'f09.F2000.ESM_Hindcast_20170911'


reg   = lonb+latb+[850, 850]
esm   =  utaiesm.TaiESMRetriever(fdir, exp, reg, iens=-1)

## 
tcpath=f'/data/C.shaoyu/ESM2025/data/TC_OUTPUT/{esm.EXP}/TC.nc'
tcpath=f'/work1/eddie7824/ESM/TC_OUTPUT/{esm.EXP}/TC.nc'
nctc = Dataset(tcpath, 'r')
for it in range(nt):
    nowtime = stime+timedelta(hours=it)
    print(it, nowtime)

    tseries_esm,  data_u = esm.get_data(nt=1, var='U850', mean=None, stime=nowtime)
    tseries_esm,  data_v = esm.get_data(nt=1, var='V850', mean=None, stime=nowtime)
    tseries_esm,  data_pr = esm.get_data(nt=1, var='PRECT', mean=None, stime=nowtime)
    data_pr *= 3600.*1000.
    tc_mask = nctc.variables['TC'][it,\
                        esm._SUBIDX[2]:esm._SUBIDX[3],\
                        esm._SUBIDX[0]:esm._SUBIDX[1]]
    tc_mask = np.where(tc_mask>0,1,0)

    # read data
    dx = (esm.LON[1] - esm.LON[0])*111000.
    dy = (esm.LAT[1] - esm.LAT[0])*111000.
    weight = np.cos(esm.LAT[:,np.newaxis]*np.pi/180.)
    data_vort = np.gradient(data_v,axis=1)/dx - np.gradient(data_u,axis=0)/dy
    data_vort *= weight
    
    plt.close('all')
    fig, proj, ax, cax0, cax1 = ptools.create_fig(reg_str)

    # ----- rainfall -----
    # CON = ax.contourf(esm.LON, esm.LAT, data_pr, 
    #                    levels=[1,3,5,10,20], colors=['k'],
    #                    transform=proj,alpha=0.7)
    # cax1.set_axis_off()

    bounds, norm, cmap = ptools.get_cmap_of_pcp(bounds=[1, 3, 5, 10, 20])
    data = np.where(data_pr>=bounds[0], data_pr, np.nan)
    PC = ax.pcolormesh(esm.LON, esm.LAT, data, 
                       norm=norm, cmap=cmap, transform=proj,
                       alpha=0.5)
    plt.colorbar(PC, cax0)

    # ----- vorticity -----
    levels=[3.5, 7.9, 12.3, 16.7, 21.1, 25.5]
    #levels = [5, 10, 50, 100]
    #CO = ax.contourf(esm.LON,esm.LAT, data_vort*1e5, levels=levels, cmap=plt.cm.YlOrBr, extend='max', transform=proj)
    #plt.colorbar(CO, cax0)
    CO = ax.contour(esm.LON,esm.LAT, data_vort*1e5, levels=levels, colors=['k'], transform=proj, linewidths=[1])
    cax1.set_axis_off()
     
    # ----- Wind -----
    skip = (slice(None, None, 5), slice(None, None, 5))
    data_mask = np.where((data_u**2+data_v**2)**0.5>=15, True, False)
    datau = np.where(data_mask, data_u, np.nan)
    QV = ax.quiver(esm.LON[skip[1]], esm.LAT[skip[0]], 
               datau[skip], data_v[skip],
               angles='xy', scale_units='xy', scale=15,
               width=0.002, headwidth=3,
               color='b', transform=proj,
              )
   
    CO = ax.contour(esm.LON,esm.LAT, tc_mask, levels=[0.5], transform=proj, linewidths=[3], colors=[(1,0,0)])
    
    plt.sca(ax)
    datestr = nowtime.strftime('%Y%m%d_%H')
    plt.title(f'{datestr}\nTaiESM_f09', loc='left', fontweight='bold', fontsize=15)
    plt.title(f'{esm.EXP}\nvort850[1e-5], preci.[mm/hr]', loc='right', fontsize=13)
    
    os.system(f'! mkdir -p ./fig/vort_taiesm/{esm.EXP}')
    plt.savefig(f'./fig/vort_taiesm/{esm.EXP}/vort_{datestr}.png', facecolor='w', bbox_inches='tight', dpi=250)






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
#exp   = 'f02.F2000.hindcast_SSTp3k'
reg   = lonb+latb+[850, 850]
esm   =  utaiesm.TaiESMRetriever(fdir, exp, reg, iens=4)
print(exp)

def get_den(iens):
    data = []
    esm.set_ens(iens)
    tcpath=f'/data/C.shaoyu/ESM2025/data/TC_OUTPUT/{esm.EXP}/TC.nc'
    nctc = Dataset(tcpath, 'r')
    stime = datetime.strptime(esm.ENS, '%Y%m%d%H')
    out_ws = np.array([])
    out_preci = np.array([])
    for it in range(240):
        nowtime = stime+timedelta(hours=it)
        print(it, nowtime)
        tc_mask = nctc.variables['TC'][it,\
                            esm._SUBIDX[2]:esm._SUBIDX[3],\
                            esm._SUBIDX[0]:esm._SUBIDX[1]]
        print(tc_mask.max(), tc_mask.min())
        if tc_mask.max()<=0: continue
        tcid_list = np.sort(np.unique(tc_mask))[1:]
        print(tcid_list)
        tseries_esm,  data_u = esm.get_data(nt=1, var='U850', mean=None, stime=nowtime)
        tseries_esm,  data_v = esm.get_data(nt=1, var='V850', mean=None, stime=nowtime)
        data_ws = np.sqrt(data_u**2+data_v**2)
        tseries_esm,  data_pr = esm.get_data(nt=1, var='PRECT', mean=None, stime=nowtime)
        data_pr *= 3600.*1000.
        for tcid in tcid_list:
            idx = np.where(tcid==tc_mask)
            
            maxws = max(data_ws[idx])
            maxrain = max(data_pr[idx])
            out_ws = np.append(out_ws, maxws)
            out_preci = np.append(out_preci, maxrain)
        print('out_ws shape: ', out_ws.shape)
    return out_ws, out_preci
#for iens in range(31):
#    get_den(iens)

with multiprocessing.Pool(processes=6) as pool:
    results = pool.starmap(get_den, [(iens,) for iens in range(len(esm.ENSLIST))])
    #results = pool.starmap(get_den, [(iens,) for iens in range(2)])

all_ws = np.array([])
all_rain = np.array([])
for i in range(len(results)):
    all_ws  = np.append(all_ws, results[i][0])
    all_rain = np.append(all_rain, results[i][1])

np.savez(f'{exp}_indiviual', ws=all_ws, rain=all_rain)

sys.exit()
plt.close('all')
fig, proj, ax, cax0, cax1 = ptools.create_fig(reg_str)
cax1.set_axis_off()

#bounds, norm, cmap = ptools.get_cmap_of_pcp(bounds=[0.1, 0.5, 1, 2, 5])
bounds, norm, cmap = ptools.get_cmap_of_pcp(bounds=[0, 5, 10, 15, 25])
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






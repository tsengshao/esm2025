import numpy as np
import os, sys
sys.path.insert(1, '../')
from utils import vinth2p as h2p
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from netCDF4 import Dataset

casename = 'f09_B1850TAI_BC2000'
dpath = f'/work1/umbrella0c/taiesm_work/archive/{casename}/atm/'
stime = datetime(1,1,1,0)
nmo   = 14
outpath = f'{dpath}/pres/'
os.makedirs(f'{outpath}', exist_ok=True)

ctl=f"""
dset ^pres/{casename}.cam.h0.%y4-%m2.nc
options template 365_day_calendar
tdef time  {nmo} linear 01{stime.strftime('%b')}{stime.year:04d} 1mo
"""
fout = open(f'{dpath}/pres_h0.ctl','w')
fout.write(ctl)
fout.close()
#sys.exit()

for imo in range(nmo):
    nowtime = stime+relativedelta(months=imo)
    print(nowtime)
    tstr    = '{:04d}-{:02d}'.format(nowtime.year, nowtime.month)
    fpath   = os.path.join(dpath,'hist',f"{casename}.cam.h0.{tstr}.nc")
    nc_h0   = Dataset(fpath,'r')
   
    fname = os.path.join(outpath, f"{casename}.cam.h0.{tstr}.nc")
    nc_out = h2p.create_nc_from_h0(nc_h0, fname)
    for varname in ['U', 'V', 'T', 'Q', 'Z3', 'OMEGA']:
        print(varname)
        var_nc  = h2p.regrid_and_save_variables(varname, nc_h0, nc_h0, nc_out)
    nc_out.close()

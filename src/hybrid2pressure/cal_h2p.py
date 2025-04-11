import numpy as np
import os, sys
sys.path.insert(1, '../')
from utils import vinth2p as h2p
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from netCDF4 import Dataset


#/work1/umbrella0c/taiesm_work/archive/f09.F2000.ESMclass.EAstrat/atm/hist/f09.F2000.ESMclass.EAstrat.cam.h1.0001-01-11-00000.nc
#f09.F2000.ESMclass.EAstrat.cam.h1.0001-01-05-00000.nc


casename = 'f09.F2000.ESMclass.ice_future'
casename = 'f09.F2000.ESMclass.ice_preindustrial'
stime = datetime(1,4,1,0)
nfile   = 12
dt_ctl  = '1mo'
dfile_time = relativedelta(months=1)
htype   = 'h0'
fmt_ctl = '%y4-%m2'
fmt_tstr = '%m'
nt_ctl   = nfile

casename='f09.F2000.ESMclass.EAstrat'
stime = datetime(1,1,1,0)
nfile   = 11
dt_ctl  = '1hr'
dfile_time = relativedelta(days=1)
htype   = 'h1'
fmt_ctl = '%y4-%m2-%d2-00000'
fmt_tstr = '%m-%d-00000'
nt_ctl   = nfile*24

dpath = f'/work1/umbrella0c/taiesm_work/archive/{casename}/atm/'
outpath = f'{dpath}/pres/'
os.makedirs(f'{outpath}', exist_ok=True)

ctl=f"""
dset ^pres/{casename}.cam.{htype}.{fmt_ctl}.nc
options template 365_day_calendar
tdef time  {nt_ctl} linear 01{stime.strftime('%b')}{stime.year:04d} {dt_ctl}
"""
fout = open(f'{dpath}/pres_{htype}.ctl','w')
fout.write(ctl)
fout.close()

for ifile in range(nfile):
    nowtime = stime+dfile_time*ifile
    print(nowtime)
    #tstr    = '{:04d}-{:02d}'.format(nowtime.year, nowtime.month)
    tstr    = f'{nowtime.year:04d}-'+nowtime.strftime(fmt_tstr)
    fpath   = os.path.join(dpath,'hist',f"{casename}.cam.{htype}.{tstr}.nc")
    nc_h0   = Dataset(fpath,'r')
   
    fname = os.path.join(outpath, f"{casename}.cam.{htype}.{tstr}.nc")
    nc_out = h2p.create_nc_from_h0(nc_h0, fname)
    for varname in ['U', 'V', 'T', 'Q', 'Z3', 'OMEGA']:
        print(varname)
        var_nc  = h2p.regrid_and_save_variables(varname, nc_h0, nc_h0, nc_out)
    nc_out.close()
